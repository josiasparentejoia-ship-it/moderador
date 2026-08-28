"""
Bot Moderador Valak Search - Versão Python
Sistema completo de administração via dashboard inline
"""
import os
import sys
import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

# Fix encoding no Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import (
    Message, CallbackQuery, ChatMemberUpdated,
    InlineKeyboardMarkup, InlineKeyboardButton,
    InputMediaPhoto, InputMediaVideo, ChatPermissions,
    WebAppInfo
)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv

load_dotenv()

# ═══════════════════════════════════════════════════════
# CONFIGURAÇÕES
# ═══════════════════════════════════════════════════════

BOT_TOKEN = os.getenv("BOT_TOKEN")
GROUP_ID = int(os.getenv("GROUP_ID"))
WEBAPP_URL = os.getenv("WEBAPP_URL")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

CONFIG_FILE = Path("config.json")

# ═══════════════════════════════════════════════════════
# ESTADOS FSM
# ═══════════════════════════════════════════════════════

class AdminStates(StatesGroup):
    # Mensagens periódicas
    creating_periodic_text = State()
    creating_periodic_interval = State()
    creating_periodic_media = State()

    # Boas-vindas
    editing_welcome_text = State()
    editing_welcome_media = State()

    # Envio grupo
    sending_group_message = State()
    sending_group_media = State()

# ═══════════════════════════════════════════════════════
# FUNÇÕES DE CONFIGURAÇÃO
# ═══════════════════════════════════════════════════════

def load_config() -> Dict[str, Any]:
    """Carrega configurações do arquivo JSON"""
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ Erro ao carregar config: {e}")

    return {
        "admin_ids": [ADMIN_ID] if ADMIN_ID else [],
        "welcome_message": {
            "text": "🎉 Bem-vindo(a), {name}!\n\nPara liberar o chat, aceite os termos do grupo.\n\n👇 Clique abaixo:",
            "media": None,
            "media_type": None,
            "button": {
                "text": "📋 ACEITE OS TERMOS",
                "url": WEBAPP_URL
            }
        },
        "periodic_messages": []
    }

def save_config(config: Dict[str, Any]) -> bool:
    """Salva configurações no arquivo JSON"""
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"❌ Erro ao salvar config: {e}")
        return False

# Carrega config inicial
config = load_config()
last_welcome_message_id = None

# ═══════════════════════════════════════════════════════
# INICIALIZAÇÃO BOT
# ═══════════════════════════════════════════════════════

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
router = Router()

# ═══════════════════════════════════════════════════════
# FUNÇÕES AUXILIARES
# ═══════════════════════════════════════════════════════

def is_admin(user_id: int) -> bool:
    """Verifica se usuário é admin"""
    return user_id in config["admin_ids"]

async def restrict_user(user_id: int):
    """Restringe usuário (apenas leitura)"""
    try:
        await bot.restrict_chat_member(
            chat_id=GROUP_ID,
            user_id=user_id,
            permissions=ChatPermissions(
                can_send_messages=False,
                can_send_media_messages=False,
                can_send_polls=False,
                can_send_other_messages=False,
                can_add_web_page_previews=False
            )
        )
        print(f"✓ Usuário {user_id} restrito")
    except Exception as e:
        print(f"✗ Erro ao restringir {user_id}: {e}")

async def unlock_user(user_id: int) -> bool:
    """Libera usuário (permissões completas)"""
    try:
        await bot.restrict_chat_member(
            chat_id=GROUP_ID,
            user_id=user_id,
            permissions=ChatPermissions(
                can_send_messages=True,
                can_send_media_messages=True,
                can_send_polls=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True,
                can_invite_users=True
            )
        )
        print(f"✓ Usuário {user_id} liberado")
        return True
    except Exception as e:
        print(f"✗ Erro ao liberar {user_id}: {e}")
        return False

# ═══════════════════════════════════════════════════════
# TECLADOS INLINE
# ═══════════════════════════════════════════════════════

def get_main_menu() -> InlineKeyboardMarkup:
    """Menu principal do admin"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📨 Mensagens Periódicas", callback_data="menu_periodic")],
        [InlineKeyboardButton(text="👋 Configurar Boas-Vindas", callback_data="menu_welcome")],
        [InlineKeyboardButton(text="📤 Enviar no Grupo", callback_data="send_group")],
        [InlineKeyboardButton(text="📊 Ver Status", callback_data="view_status")],
        [InlineKeyboardButton(text="❌ Fechar", callback_data="close_menu")]
    ])

def get_periodic_menu() -> InlineKeyboardMarkup:
    """Menu de mensagens periódicas"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Nova Mensagem", callback_data="periodic_new")],
        [InlineKeyboardButton(text="📋 Listar Mensagens", callback_data="periodic_list")],
        [InlineKeyboardButton(text="🔙 Voltar", callback_data="menu_main")]
    ])

def get_welcome_menu() -> InlineKeyboardMarkup:
    """Menu de boas-vindas"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✏️ Editar Texto", callback_data="welcome_edit_text")],
        [InlineKeyboardButton(text="🖼️ Adicionar Mídia", callback_data="welcome_add_media")],
        [InlineKeyboardButton(text="🗑️ Remover Mídia", callback_data="welcome_remove_media")],
        [InlineKeyboardButton(text="👁️ Visualizar", callback_data="welcome_preview")],
        [InlineKeyboardButton(text="🔙 Voltar", callback_data="menu_main")]
    ])

# ═══════════════════════════════════════════════════════
# COMANDO /ADMIN - DASHBOARD
# ═══════════════════════════════════════════════════════

@router.message(Command("admin"))
async def cmd_admin(message: Message):
    """Abre o painel administrativo"""
    if not is_admin(message.from_user.id):
        await message.answer("❌ Você não tem permissão para acessar o painel admin.")
        return

    await message.answer(
        "🎛️ <b>PAINEL ADMINISTRATIVO</b>\n\n"
        "Bem-vindo ao painel de controle do bot!\n"
        "Use os botões abaixo para gerenciar o grupo:",
        parse_mode="HTML",
        reply_markup=get_main_menu()
    )

# ═══════════════════════════════════════════════════════
# CALLBACKS - MENUS
# ═══════════════════════════════════════════════════════

@router.callback_query(F.data == "menu_main")
async def callback_menu_main(callback: CallbackQuery):
    """Volta ao menu principal"""
    await callback.message.edit_text(
        "🎛️ <b>PAINEL ADMINISTRATIVO</b>\n\n"
        "Bem-vindo ao painel de controle do bot!\n"
        "Use os botões abaixo para gerenciar o grupo:",
        parse_mode="HTML",
        reply_markup=get_main_menu()
    )
    await callback.answer()

@router.callback_query(F.data == "menu_periodic")
async def callback_menu_periodic(callback: CallbackQuery):
    """Menu de mensagens periódicas"""
    active = len([m for m in config["periodic_messages"] if m.get("enabled", True)])
    total = len(config["periodic_messages"])

    await callback.message.edit_text(
        f"📨 <b>MENSAGENS PERIÓDICAS</b>\n\n"
        f"Total de mensagens ativas: <b>{active}</b>\n"
        f"Total cadastradas: <b>{total}</b>",
        parse_mode="HTML",
        reply_markup=get_periodic_menu()
    )
    await callback.answer()

@router.callback_query(F.data == "menu_welcome")
async def callback_menu_welcome(callback: CallbackQuery):
    """Menu de boas-vindas"""
    welcome = config["welcome_message"]
    text_preview = welcome["text"][:100] + "..." if len(welcome["text"]) > 100 else welcome["text"]

    await callback.message.edit_text(
        "👋 <b>MENSAGEM DE BOAS-VINDAS</b>\n\n"
        f"<b>Texto atual:</b>\n{text_preview}\n\n"
        f"<b>Mídia:</b> {'✅ Configurada' if welcome.get('media') else '❌ Sem mídia'}",
        parse_mode="HTML",
        reply_markup=get_welcome_menu()
    )
    await callback.answer()

@router.callback_query(F.data == "close_menu")
async def callback_close_menu(callback: CallbackQuery):
    """Fecha o menu"""
    await callback.message.delete()
    await callback.answer("✅ Menu fechado")

# ═══════════════════════════════════════════════════════
# MENSAGENS PERIÓDICAS - CRIAR
# ═══════════════════════════════════════════════════════

@router.callback_query(F.data == "periodic_new")
async def callback_periodic_new(callback: CallbackQuery, state: FSMContext):
    """Inicia criação de mensagem periódica"""
    await state.set_state(AdminStates.creating_periodic_text)

    await callback.message.edit_text(
        "✏️ <b>NOVA MENSAGEM PERIÓDICA</b>\n\n"
        "📝 Envie o texto da mensagem.\n\n"
        "Você pode usar:\n"
        "• Emojis\n"
        "• Formatação HTML\n"
        "• Quebras de linha\n\n"
        "💡 Envie /cancelar para cancelar",
        parse_mode="HTML"
    )
    await callback.answer()

@router.message(AdminStates.creating_periodic_text)
async def process_periodic_text(message: Message, state: FSMContext):
    """Recebe texto da mensagem periódica"""
    await state.update_data(text=message.text)
    await state.set_state(AdminStates.creating_periodic_interval)

    await message.answer(
        "⏰ <b>INTERVALO DA MENSAGEM</b>\n\n"
        "Digite o intervalo em <b>minutos</b> entre cada envio.\n\n"
        "<b>Exemplos:</b>\n"
        "• 60 = 1 hora\n"
        "• 180 = 3 horas\n"
        "• 1440 = 1 dia\n\n"
        "💡 Envie /cancelar para cancelar",
        parse_mode="HTML"
    )

@router.message(AdminStates.creating_periodic_interval)
async def process_periodic_interval(message: Message, state: FSMContext):
    """Recebe intervalo e pergunta sobre mídia"""
    try:
        interval = int(message.text)
        if interval < 1:
            raise ValueError
    except ValueError:
        await message.answer("❌ Intervalo inválido! Digite um número maior que 0.")
        return

    await state.update_data(interval=interval)
    await state.set_state(AdminStates.creating_periodic_media)

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⏭️ Pular (sem mídia)", callback_data="periodic_skip_media")]
    ])

    await message.answer(
        "🖼️ <b>ADICIONAR MÍDIA?</b>\n\n"
        "📤 Envie uma <b>foto</b> ou <b>vídeo</b> para acompanhar a mensagem.\n\n"
        "Ou clique em 'Pular' para criar sem mídia.\n\n"
        "💡 Envie /cancelar para cancelar",
        parse_mode="HTML",
        reply_markup=keyboard
    )

@router.callback_query(F.data == "periodic_skip_media", AdminStates.creating_periodic_media)
async def callback_periodic_skip_media(callback: CallbackQuery, state: FSMContext):
    """Cria mensagem sem mídia"""
    data = await state.get_data()

    new_message = {
        "id": int(datetime.now().timestamp() * 1000),
        "text": data["text"],
        "media": None,
        "media_type": None,
        "interval": data["interval"],
        "enabled": True,
        "created_at": datetime.now().isoformat()
    }

    config["periodic_messages"].append(new_message)
    save_config(config)
    await state.clear()

    await callback.message.edit_text(
        "✅ <b>MENSAGEM CRIADA COM SUCESSO!</b>\n\n"
        f"📝 Texto: {data['text'][:50]}...\n"
        f"⏰ Intervalo: {data['interval']} minutos\n"
        f"🎯 Status: Ativa",
        parse_mode="HTML",
        reply_markup=get_main_menu()
    )
    await callback.answer()

@router.message(AdminStates.creating_periodic_media, F.photo)
async def process_periodic_photo(message: Message, state: FSMContext):
    """Recebe foto para mensagem periódica"""
    data = await state.get_data()
    file_id = message.photo[-1].file_id

    new_message = {
        "id": int(datetime.now().timestamp() * 1000),
        "text": data["text"],
        "media": file_id,
        "media_type": "photo",
        "interval": data["interval"],
        "enabled": True,
        "created_at": datetime.now().isoformat()
    }

    config["periodic_messages"].append(new_message)
    save_config(config)
    await state.clear()

    await message.answer(
        "✅ <b>MENSAGEM CRIADA COM SUCESSO!</b>\n\n"
        f"📝 Texto: {data['text'][:50]}...\n"
        f"🖼️ Mídia: Foto\n"
        f"⏰ Intervalo: {data['interval']} minutos\n"
        f"🎯 Status: Ativa",
        parse_mode="HTML",
        reply_markup=get_main_menu()
    )

@router.message(AdminStates.creating_periodic_media, F.video)
async def process_periodic_video(message: Message, state: FSMContext):
    """Recebe vídeo para mensagem periódica"""
    data = await state.get_data()
    file_id = message.video.file_id

    new_message = {
        "id": int(datetime.now().timestamp() * 1000),
        "text": data["text"],
        "media": file_id,
        "media_type": "video",
        "interval": data["interval"],
        "enabled": True,
        "created_at": datetime.now().isoformat()
    }

    config["periodic_messages"].append(new_message)
    save_config(config)
    await state.clear()

    await message.answer(
        "✅ <b>MENSAGEM CRIADA COM SUCESSO!</b>\n\n"
        f"📝 Texto: {data['text'][:50]}...\n"
        f"🎬 Mídia: Vídeo\n"
        f"⏰ Intervalo: {data['interval']} minutos\n"
        f"🎯 Status: Ativa",
        parse_mode="HTML",
        reply_markup=get_main_menu()
    )

# ═══════════════════════════════════════════════════════
# MENSAGENS PERIÓDICAS - LISTAR
# ═══════════════════════════════════════════════════════

@router.callback_query(F.data == "periodic_list")
async def callback_periodic_list(callback: CallbackQuery):
    """Lista mensagens periódicas"""
    if not config["periodic_messages"]:
        await callback.message.edit_text(
            "📋 <b>MENSAGENS PERIÓDICAS</b>\n\n"
            "❌ Nenhuma mensagem cadastrada.",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 Voltar", callback_data="menu_periodic")]
            ])
        )
        await callback.answer()
        return

    text = "📋 <b>MENSAGENS CADASTRADAS</b>\n\n"
    buttons = []

    for idx, msg in enumerate(config["periodic_messages"]):
        status = "✅" if msg.get("enabled", True) else "⏸️"
        preview = msg["text"][:40].replace("\n", " ")
        media_icon = {"photo": "🖼️", "video": "🎬"}.get(msg.get("media_type"), "")

        text += f"{status} <b>#{idx + 1}</b> {media_icon} {preview}...\n"
        text += f"   ⏰ Intervalo: {msg['interval']} min\n\n"

        buttons.append([
            InlineKeyboardButton(
                text=f"{'⏸️ Pausar' if msg.get('enabled', True) else '▶️ Ativar'} #{idx + 1}",
                callback_data=f"periodic_toggle_{idx}"
            ),
            InlineKeyboardButton(
                text=f"🗑️ Deletar #{idx + 1}",
                callback_data=f"periodic_delete_{idx}"
            )
        ])

    buttons.append([InlineKeyboardButton(text="🔙 Voltar", callback_data="menu_periodic")])

    await callback.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
    )
    await callback.answer()

@router.callback_query(F.data.startswith("periodic_toggle_"))
async def callback_periodic_toggle(callback: CallbackQuery):
    """Ativa/pausa mensagem periódica"""
    idx = int(callback.data.split("_")[-1])

    if idx < len(config["periodic_messages"]):
        config["periodic_messages"][idx]["enabled"] = not config["periodic_messages"][idx].get("enabled", True)
        save_config(config)

        status = "✅ Ativada" if config["periodic_messages"][idx]["enabled"] else "⏸️ Pausada"
        await callback.answer(f"{status}!")

        # Atualiza a lista
        await callback_periodic_list(callback)

@router.callback_query(F.data.startswith("periodic_delete_"))
async def callback_periodic_delete(callback: CallbackQuery):
    """Deleta mensagem periódica"""
    idx = int(callback.data.split("_")[-1])

    if idx < len(config["periodic_messages"]):
        config["periodic_messages"].pop(idx)
        save_config(config)

        await callback.answer("🗑️ Mensagem deletada!")

        # Atualiza a lista
        await callback_periodic_list(callback)

# ═══════════════════════════════════════════════════════
# BOAS-VINDAS - EDITAR
# ═══════════════════════════════════════════════════════

@router.callback_query(F.data == "welcome_edit_text")
async def callback_welcome_edit_text(callback: CallbackQuery, state: FSMContext):
    """Edita texto de boas-vindas"""
    await state.set_state(AdminStates.editing_welcome_text)

    await callback.message.edit_text(
        "✏️ <b>EDITAR MENSAGEM DE BOAS-VINDAS</b>\n\n"
        "📝 Envie o novo texto.\n\n"
        "<b>Use:</b>\n"
        "• <code>{name}</code> - nome do usuário\n"
        "• Emojis e formatação HTML\n\n"
        "💡 Envie /cancelar para cancelar",
        parse_mode="HTML"
    )
    await callback.answer()

@router.message(AdminStates.editing_welcome_text)
async def process_welcome_text(message: Message, state: FSMContext):
    """Salva novo texto de boas-vindas"""
    config["welcome_message"]["text"] = message.text
    save_config(config)
    await state.clear()

    await message.answer(
        "✅ Mensagem de boas-vindas atualizada!",
        reply_markup=get_main_menu()
    )

@router.callback_query(F.data == "welcome_add_media")
async def callback_welcome_add_media(callback: CallbackQuery, state: FSMContext):
    """Adiciona mídia à boas-vindas"""
    await state.set_state(AdminStates.editing_welcome_media)

    await callback.message.edit_text(
        "🖼️ <b>ADICIONAR MÍDIA</b>\n\n"
        "📤 Envie uma <b>foto</b> ou <b>vídeo</b>.\n\n"
        "💡 Envie /cancelar para cancelar",
        parse_mode="HTML"
    )
    await callback.answer()

@router.message(AdminStates.editing_welcome_media, F.photo)
async def process_welcome_photo(message: Message, state: FSMContext):
    """Salva foto de boas-vindas"""
    file_id = message.photo[-1].file_id
    config["welcome_message"]["media"] = file_id
    config["welcome_message"]["media_type"] = "photo"
    save_config(config)
    await state.clear()

    await message.answer(
        "✅ Foto adicionada à mensagem de boas-vindas!",
        reply_markup=get_main_menu()
    )

@router.message(AdminStates.editing_welcome_media, F.video)
async def process_welcome_video(message: Message, state: FSMContext):
    """Salva vídeo de boas-vindas"""
    file_id = message.video.file_id
    config["welcome_message"]["media"] = file_id
    config["welcome_message"]["media_type"] = "video"
    save_config(config)
    await state.clear()

    await message.answer(
        "✅ Vídeo adicionado à mensagem de boas-vindas!",
        reply_markup=get_main_menu()
    )

@router.callback_query(F.data == "welcome_remove_media")
async def callback_welcome_remove_media(callback: CallbackQuery):
    """Remove mídia de boas-vindas"""
    config["welcome_message"]["media"] = None
    config["welcome_message"]["media_type"] = None
    save_config(config)

    await callback.answer("✅ Mídia removida!")
    await callback_menu_welcome(callback)

@router.callback_query(F.data == "welcome_preview")
async def callback_welcome_preview(callback: CallbackQuery):
    """Visualiza mensagem de boas-vindas"""
    await callback.answer()

    welcome = config["welcome_message"]
    text = welcome["text"].replace("{name}", callback.from_user.first_name)

    keyboard = None
    if welcome.get("button", {}).get("url"):
        keyboard = InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(
                text=welcome["button"]["text"],
                url=welcome["button"]["url"]
            )
        ]])

    if welcome.get("media"):
        if welcome["media_type"] == "photo":
            await callback.message.answer_photo(
                photo=welcome["media"],
                caption=text,
                parse_mode="HTML",
                reply_markup=keyboard
            )
        elif welcome["media_type"] == "video":
            await callback.message.answer_video(
                video=welcome["media"],
                caption=text,
                parse_mode="HTML",
                reply_markup=keyboard
            )
    else:
        await callback.message.answer(
            text,
            parse_mode="HTML",
            reply_markup=keyboard
        )

# ═══════════════════════════════════════════════════════
# ENVIAR MENSAGEM NO GRUPO
# ═══════════════════════════════════════════════════════

@router.callback_query(F.data == "send_group")
async def callback_send_group(callback: CallbackQuery, state: FSMContext):
    """Inicia envio de mensagem no grupo"""
    await state.set_state(AdminStates.sending_group_message)

    await callback.message.edit_text(
        "📤 <b>ENVIAR MENSAGEM NO GRUPO</b>\n\n"
        "📝 Envie o texto da mensagem.\n\n"
        "Você pode enviar:\n"
        "• Texto simples\n"
        "• Foto com legenda (envie a foto)\n"
        "• Vídeo com legenda (envie o vídeo)\n\n"
        "💡 Envie /cancelar para cancelar",
        parse_mode="HTML"
    )
    await callback.answer()

@router.message(AdminStates.sending_group_message, F.text)
async def process_send_group_text(message: Message, state: FSMContext):
    """Envia texto no grupo"""
    try:
        await bot.send_message(
            chat_id=GROUP_ID,
            text=message.text,
            parse_mode="HTML"
        )
        await state.clear()

        await message.answer(
            "✅ Mensagem enviada no grupo!",
            reply_markup=get_main_menu()
        )
    except Exception as e:
        await message.answer(f"❌ Erro ao enviar: {e}")

@router.message(AdminStates.sending_group_message, F.photo)
async def process_send_group_photo(message: Message, state: FSMContext):
    """Envia foto no grupo"""
    try:
        await bot.send_photo(
            chat_id=GROUP_ID,
            photo=message.photo[-1].file_id,
            caption=message.caption or "",
            parse_mode="HTML"
        )
        await state.clear()

        await message.answer(
            "✅ Foto enviada no grupo!",
            reply_markup=get_main_menu()
        )
    except Exception as e:
        await message.answer(f"❌ Erro ao enviar: {e}")

@router.message(AdminStates.sending_group_message, F.video)
async def process_send_group_video(message: Message, state: FSMContext):
    """Envia vídeo no grupo"""
    try:
        await bot.send_video(
            chat_id=GROUP_ID,
            video=message.video.file_id,
            caption=message.caption or "",
            parse_mode="HTML"
        )
        await state.clear()

        await message.answer(
            "✅ Vídeo enviado no grupo!",
            reply_markup=get_main_menu()
        )
    except Exception as e:
        await message.answer(f"❌ Erro ao enviar: {e}")

# ═══════════════════════════════════════════════════════
# STATUS
# ═══════════════════════════════════════════════════════

@router.callback_query(F.data == "view_status")
async def callback_view_status(callback: CallbackQuery):
    """Mostra status do bot"""
    active = len([m for m in config["periodic_messages"] if m.get("enabled", True)])
    total = len(config["periodic_messages"])

    status_text = (
        "📊 <b>STATUS DO BOT</b>\n\n"
        f"🤖 Bot: <b>Online ✅</b>\n"
        f"👥 Grupo: <b>{GROUP_ID}</b>\n"
        f"👑 Admins: <b>{len(config['admin_ids'])}</b>\n\n"
        f"📨 Mensagens periódicas ativas: <b>{active}</b>\n"
        f"📋 Total cadastradas: <b>{total}</b>\n\n"
        f"👋 Boas-vindas: <b>{'Com mídia' if config['welcome_message'].get('media') else 'Apenas texto'}</b>"
    )

    await callback.message.edit_text(
        status_text,
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Voltar", callback_data="menu_main")]
        ])
    )
    await callback.answer()

# ═══════════════════════════════════════════════════════
# COMANDO /CANCELAR
# ═══════════════════════════════════════════════════════

@router.message(Command("cancelar"))
async def cmd_cancelar(message: Message, state: FSMContext):
    """Cancela operação atual"""
    await state.clear()
    await message.answer(
        "❌ Ação cancelada!",
        reply_markup=get_main_menu()
    )

# ═══════════════════════════════════════════════════════
# NOVOS MEMBROS - BOAS-VINDAS
# ═══════════════════════════════════════════════════════

@router.chat_member()
async def on_chat_member(event: ChatMemberUpdated):
    """Detecta novos membros"""
    global last_welcome_message_id

    old_status = event.old_chat_member.status
    new_status = event.new_chat_member.status
    user = event.new_chat_member.user

    if old_status in ["left", "kicked"] and new_status in ["member", "administrator"]:
        print(f"\n📥 Novo membro: {user.first_name} ({user.id})")

        # Apaga mensagem anterior
        if last_welcome_message_id:
            try:
                await bot.delete_message(GROUP_ID, last_welcome_message_id)
            except:
                pass

        # Restringe usuário
        await restrict_user(user.id)

        # Envia boas-vindas
        welcome = config["welcome_message"]
        text = welcome["text"].replace("{name}", user.first_name)

        keyboard = None
        if welcome.get("button", {}).get("url"):
            keyboard = InlineKeyboardMarkup(inline_keyboard=[[
                InlineKeyboardButton(
                    text=welcome["button"]["text"],
                    web_app=WebAppInfo(url=welcome["button"]["url"])
                )
            ]])

        try:
            if welcome.get("media"):
                if welcome["media_type"] == "photo":
                    message = await bot.send_photo(
                        chat_id=GROUP_ID,
                        photo=welcome["media"],
                        caption=text,
                        parse_mode="HTML",
                        reply_markup=keyboard
                    )
                elif welcome["media_type"] == "video":
                    message = await bot.send_video(
                        chat_id=GROUP_ID,
                        video=welcome["media"],
                        caption=text,
                        parse_mode="HTML",
                        reply_markup=keyboard
                    )
            else:
                message = await bot.send_message(
                    chat_id=GROUP_ID,
                    text=text,
                    parse_mode="HTML",
                    reply_markup=keyboard
                )

            last_welcome_message_id = message.message_id
            print("✓ Mensagem de boas-vindas enviada")
        except Exception as e:
            print(f"✗ Erro ao enviar boas-vindas: {e}")

# ═══════════════════════════════════════════════════════
# SISTEMA DE MENSAGENS PERIÓDICAS
# ═══════════════════════════════════════════════════════

async def send_periodic_messages():
    """Envia mensagens periódicas (background task)"""
    print("⏰ Sistema de mensagens periódicas iniciado")

    # Dicionário para rastrear último envio de cada mensagem
    last_sent = {}

    while True:
        try:
            now = datetime.now()

            for msg in config["periodic_messages"]:
                if not msg.get("enabled", True):
                    continue

                msg_id = msg["id"]
                interval_minutes = msg["interval"]

                # Verifica se já passou o intervalo
                if msg_id in last_sent:
                    elapsed = (now - last_sent[msg_id]).total_seconds() / 60
                    if elapsed < interval_minutes:
                        continue

                # Envia mensagem
                try:
                    if msg.get("media"):
                        if msg["media_type"] == "photo":
                            await bot.send_photo(
                                chat_id=GROUP_ID,
                                photo=msg["media"],
                                caption=msg["text"],
                                parse_mode="HTML"
                            )
                        elif msg["media_type"] == "video":
                            await bot.send_video(
                                chat_id=GROUP_ID,
                                video=msg["media"],
                                caption=msg["text"],
                                parse_mode="HTML"
                            )
                    else:
                        await bot.send_message(
                            chat_id=GROUP_ID,
                            text=msg["text"],
                            parse_mode="HTML"
                        )

                    last_sent[msg_id] = now
                    print(f"✓ Mensagem periódica enviada: {msg['text'][:30]}...")
                except Exception as e:
                    print(f"✗ Erro ao enviar mensagem periódica: {e}")

            # Aguarda 1 minuto antes de verificar novamente
            await asyncio.sleep(60)

        except Exception as e:
            print(f"✗ Erro no sistema de mensagens periódicas: {e}")
            await asyncio.sleep(60)

# ═══════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════

async def main():
    """Função principal"""
    # Registra router
    dp.include_router(router)

    # Inicia task de mensagens periódicas
    asyncio.create_task(send_periodic_messages())

    print("🤖 Bot iniciado com sucesso!")
    print(f"📱 Monitorando grupo: {GROUP_ID}")
    print(f"👑 Admins configurados: {len(config['admin_ids'])}")
    print("\n💡 Use /admin no privado do bot para acessar o painel\n")

    # Inicia polling
    await dp.start_polling(bot, allowed_updates=["message", "callback_query", "chat_member"])

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Bot encerrado")
