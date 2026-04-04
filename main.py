"""
Ponto de entrada único: sobe o FastAPI (uvicorn) + o bot (aiogram)
em threads separadas dentro do mesmo processo Railway.
"""
import asyncio
import threading
import os
import uvicorn
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN  = os.environ.get("BOT_TOKEN")
WEBAPP_URL = os.environ.get("WEBAPP_URL")
PORT       = int(os.environ.get("PORT", 8000))

# Diagnóstico de startup
print(f"[startup] BOT_TOKEN definido: {bool(BOT_TOKEN)}")
print(f"[startup] WEBAPP_URL: {WEBAPP_URL}")
print(f"[startup] PORT: {PORT}")

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN não encontrado nas variáveis de ambiente!")


def run_api():
    uvicorn.run("server:app", host="0.0.0.0", port=PORT, log_level="info")


ADMIN_ID = int(os.environ.get("ADMIN_ID", 0))

async def run_bot():
    from aiogram import Bot, Dispatcher
    from aiogram.filters import CommandStart, Command
    from aiogram.types import (
        Message, ChatJoinRequest,
        InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
    )
    from database import init_db, user_accepted, ban_user, unban_user, list_users

    bot = Bot(token=BOT_TOKEN)
    dp  = Dispatcher()
    init_db()

    def is_admin(message: Message) -> bool:
        return message.from_user.id == ADMIN_ID

    @dp.message(CommandStart())
    async def cmd_start(message: Message):
        kb = InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(
                text="📜 Acessar termos",
                web_app=WebAppInfo(url=WEBAPP_URL)
            )
        ]])
        await message.answer(
            "👋 Olá! Para entrar no grupo você precisa ler e aceitar os termos.\n\n"
            "Clique no botão abaixo para continuar:",
            reply_markup=kb
        )

    @dp.message(Command("usuarios"))
    async def cmd_usuarios(message: Message):
        if not is_admin(message):
            return
        rows = list_users(10)
        if not rows:
            await message.answer("Nenhum usuário registrado ainda.")
            return
        txt = "👥 *Últimos 10 usuários:*\n\n"
        for uid, username, first_name, ip, accepted_at, banned in rows:
            status = "🚫 banido" if banned else "✅ ativo"
            nome = f"@{username}" if username else first_name or "?"
            txt += (
                f"{status} {nome}\n"
                f"  ID: `{uid}`\n"
                f"  IP: `{ip}`\n"
                f"  Em: {accepted_at[:16] if accepted_at else '?'}\n\n"
            )
        await message.answer(txt, parse_mode="Markdown")

    @dp.message(Command("bloquear"))
    async def cmd_bloquear(message: Message):
        if not is_admin(message):
            return
        args = message.text.split()
        if len(args) < 2 or not args[1].isdigit():
            await message.answer("Uso: /bloquear <user_id>")
            return
        uid = int(args[1])
        ban_user(uid)
        try:
            await bot.ban_chat_member(int(os.environ.get("CHAT_ID")), uid)
        except Exception:
            pass
        await message.answer(f"🚫 Usuário `{uid}` bloqueado e removido do grupo.", parse_mode="Markdown")

    @dp.message(Command("desbloquear"))
    async def cmd_desbloquear(message: Message):
        if not is_admin(message):
            return
        args = message.text.split()
        if len(args) < 2 or not args[1].isdigit():
            await message.answer("Uso: /desbloquear <user_id>")
            return
        uid = int(args[1])
        unban_user(uid)
        try:
            await bot.unban_chat_member(int(os.environ.get("CHAT_ID")), uid)
        except Exception:
            pass
        await message.answer(f"✅ Usuário `{uid}` desbloqueado.", parse_mode="Markdown")

    @dp.chat_join_request()
    async def handle_join_request(request: ChatJoinRequest):
        uid = request.from_user.id
        if user_accepted(uid):
            await bot.approve_chat_join_request(request.chat.id, uid)
        else:
            await bot.decline_chat_join_request(request.chat.id, uid)
            await bot.send_message(
                uid,
                "❌ Solicitação recusada.\n"
                "Aceite os termos primeiro. Use /start para começar."
            )

    print("[bot] Polling iniciado...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    t = threading.Thread(target=run_api, daemon=True)
    t.start()
    asyncio.run(run_bot())
