from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from database.db import add_user, get_user_language, set_user_language
from translations import get_text
from utils.keyboards import get_language_keyboard, get_main_keyboard

router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    user_id = message.from_user.id
    username = message.from_user.username or "User"
    add_user(user_id, username)
    
    lang = get_user_language(user_id)
    text = get_text(lang, 'welcome', username=username)
    await message.answer(text, reply_markup=get_language_keyboard())

@router.callback_query(F.data.startswith('lang_'))
async def process_language_selection(callback: CallbackQuery):
    user_id = callback.from_user.id
    selected_lang = callback.data.split('_')[1]
    
    set_user_language(user_id, selected_lang)
    
    await callback.message.edit_text(get_text(selected_lang, 'language_selected'))
    await callback.message.answer(
        get_text(selected_lang, 'main_menu'),
        reply_markup=get_main_keyboard(selected_lang)
    )
    await callback.answer()

@router.message(F.text.in_(['❓ Yordam', '❓ Помощь', '❓ Help']))
async def btn_help(message: Message):
    user_id = message.from_user.id
    lang = get_user_language(user_id)
    text = get_text(lang, 'help_text')
    await message.answer(text)

@router.message(F.text.in_(['🌍 Til', '🌍 Язык', '🌍 Language']))
async def btn_language(message: Message):
    user_id = message.from_user.id
    lang = get_user_language(user_id)
    text = get_text(lang, 'welcome', username=message.from_user.first_name or "User")
    await message.answer(text, reply_markup=get_language_keyboard())

def register_handlers(dp):
    dp.include_router(router)
