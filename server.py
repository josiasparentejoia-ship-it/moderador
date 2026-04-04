import hashlib
import hmac
import json
import os
import time
from urllib.parse import unquote, parse_qsl

import httpx
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse

from database import init_db, ip_already_used, user_accepted, save_user

BOT_TOKEN  = os.environ.get("BOT_TOKEN")
CHAT_ID    = os.environ.get("CHAT_ID")
LINK_EXPIRE_SECONDS = int(os.environ.get("LINK_EXPIRE_SECONDS", 300))

app = FastAPI()

init_db()

# ── Serve o index.html na raiz ──────────────────────────────────────────────
with open("index.html", encoding="utf-8") as f:
    HTML_PAGE = f.read()

@app.get("/", response_class=HTMLResponse)
async def root():
    return HTML_PAGE


# ── Validação do initData do Telegram ──────────────────────────────────────
def validate_init_data(init_data: str) -> dict | None:
    """
    Valida a assinatura do Telegram e retorna o dict com os dados do usuário.
    Retorna None se inválido.
    """
    try:
        params = dict(parse_qsl(init_data, keep_blank_values=True))
        received_hash = params.pop("hash", None)
        if not received_hash:
            return None

        # Monta a data-check-string em ordem alfabética
        data_check = "\n".join(f"{k}={v}" for k, v in sorted(params.items()))

        secret_key = hmac.new(b"WebAppData", BOT_TOKEN.encode(), hashlib.sha256).digest()
        computed   = hmac.new(secret_key, data_check.encode(), hashlib.sha256).hexdigest()

        if not hmac.compare_digest(computed, received_hash):
            return None

        # Verifica se não expirou (10 min de tolerância)
        auth_date = int(params.get("auth_date", 0))
        if time.time() - auth_date > 600:
            return None

        user = json.loads(unquote(params.get("user", "{}")))
        return user
    except Exception:
        return None


# ── Gera link de convite via Bot API ───────────────────────────────────────
async def create_invite_link() -> str:
    expire_date = int(time.time()) + LINK_EXPIRE_SECONDS
    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/createChatInviteLink",
            json={
                "chat_id":      CHAT_ID,
                "member_limit": 1,
                "expire_date":  expire_date,
                "creates_join_request": True,   # requer aprovação manual pelo bot
            }
        )
    data = r.json()
    if not data.get("ok"):
        raise RuntimeError(data.get("description", "Erro ao criar link"))
    return data["result"]["invite_link"]


# ── Endpoint principal ─────────────────────────────────────────────────────
@app.post("/api/agree")
async def agree(request: Request):
    body = await request.json()
    init_data: str = body.get("initData", "")

    # 1. Valida assinatura do Telegram
    user = validate_init_data(init_data)
    if not user:
        return JSONResponse({"error": "initData inválido"}, status_code=403)

    user_id    = user.get("id")
    username   = user.get("username", "")
    first_name = user.get("first_name", "")

    # 2. Captura IP real (respeita proxy/Nginx)
    ip = (
        request.headers.get("X-Forwarded-For", "").split(",")[0].strip()
        or request.headers.get("X-Real-IP", "")
        or request.client.host
    )

    # 3. Bloqueia se IP já foi usado
    if ip_already_used(ip):
        return JSONResponse(
            {"error": "Este dispositivo já possui acesso registrado."},
            status_code=409
        )

    # 4. Se já aceitou antes (mesmo user_id), só retorna o link salvo
    # — evita gerar links duplicados para o mesmo usuário
    if user_accepted(user_id):
        return JSONResponse({"error": "Você já aceitou os termos anteriormente."}, status_code=409)

    # 5. Gera link exclusivo
    try:
        invite_link = await create_invite_link()
    except RuntimeError as e:
        return JSONResponse({"error": str(e)}, status_code=500)

    # 6. Persiste no banco
    save_user(user_id, username, first_name, ip, invite_link)

    return JSONResponse({"invite_link": invite_link})
