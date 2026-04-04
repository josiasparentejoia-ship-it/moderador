"""
Ponto de entrada único: sobe o FastAPI (uvicorn) + o bot (aiogram)
em threads separadas dentro do mesmo processo Railway.
"""
import asyncio
import threading
import os
import uvicorn

# Lê direto do ambiente (Railway injeta as vars no container)
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


async def run_bot():
    from aiogram import Bot, Dispatcher
    from aiogram.filters import CommandStart
    from aiogram.types import (
        Message, ChatJoinRequest,
        InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
    )
    from database import init_db, user_accepted

    bot = Bot(token=BOT_TOKEN)
    dp  = Dispatcher()
    init_db()

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
