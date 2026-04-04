import os
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from dotenv import load_dotenv

from database import init_db, user_accepted

load_dotenv()

BOT_TOKEN  = os.getenv("BOT_TOKEN")
WEBAPP_URL = os.getenv("WEBAPP_URL")   # URL pública do seu server.py (HTTPS obrigatório)

bot = Bot(token=BOT_TOKEN)
dp  = Dispatcher()

init_db()


# ── /start → abre o Web App ────────────────────────────────────────────────
@dp.message(CommandStart())
async def cmd_start(message: types.Message):
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


# ── Aprova/rejeita solicitações de entrada ─────────────────────────────────
@dp.chat_join_request()
async def handle_join_request(request: types.ChatJoinRequest):
    user_id = request.from_user.id

    if user_accepted(user_id):
        await bot.approve_chat_join_request(request.chat.id, user_id)
    else:
        await bot.decline_chat_join_request(request.chat.id, user_id)
        await bot.send_message(
            user_id,
            "❌ Sua solicitação foi recusada.\n"
            "Você precisa aceitar os termos primeiro. Use /start para começar."
        )


async def main():
    print("Bot iniciado...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
