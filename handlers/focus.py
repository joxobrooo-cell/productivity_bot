from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from utils.scheduler import start_focus_session, stop_focus_session, active_sessions
from database.db import get_user_language, update_weekly_stats
from translations import get_text
from utils.keyboards import get_focus_keyboard

router = Router()

@router.message(F.text.in_(['🎯 Fokus rejim', '🎯 Режим фокуса', '🎯 Focus Mode']))
async def btn_focus(message: Message):
    user_id = message.from_user.id
    lang = get_user_language(user_id)
    
    if user_id in active_sessions:
        remaining = active_sessions[user_id].get('remaining', 25)
        await message.answer(
            get_text(lang, 'focus_running', remaining=remaining),
            reply_markup=get_focus_keyboard(lang)
        )
        return
    
    await start_focus_session(user_id, message.bot, lang)
    update_weekly_stats(user_id, 'focus')
    
    await message.answer(
        get_text(lang, 'focus_started'),
        reply_markup=get_focus_keyboard(lang)
    )

@router.callback_query(F.data == 'stop_focus')
async def process_stop_focus(callback: CallbackQuery):
    user_id = callback.from_user.id
    lang = get_user_language(user_id)
    
    if user_id not in active_sessions:
        await callback.answer(get_text(lang, 'focus_not_running'), show_alert=True)
        return
    
    stop_focus_session(user_id)
    await callback.message.edit_text(get_text(lang, 'focus_stopped'))
    await callback.answer()

def register_handlers(dp):
    dp.include_router(router)
