from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from database.db import get_user_language, get_user_settings, update_user_settings
from translations import get_text
from utils.keyboards import get_language_keyboard

router = Router()

@router.message(F.text.in_(['⚙️ Sozlamalar', '⚙️ Настройки', '⚙️ Settings']))
async def btn_settings(message: Message):
    user_id = message.from_user.id
    lang = get_user_language(user_id)
    settings = get_user_settings(user_id)
    
    notif_status = get_text(lang, 'notifications_enabled') if settings['notifications'] else get_text(lang, 'notifications_disabled')
    
    text = get_text(lang, 'settings',
                   notifications=notif_status,
                   time=settings['notification_time'],
                   language=settings['language'].upper())
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="🔔 " + ("OFF" if settings['notifications'] else "ON"),
                callback_data="toggle_notifications"
            )
        ],
        [
            InlineKeyboardButton(text=get_text(lang, 'btn_language'), callback_data="change_language")
        ]
    ])
    
    await message.answer(text, reply_markup=keyboard)

@router.callback_query(F.data == 'toggle_notifications')
async def toggle_notifications(callback: CallbackQuery):
    user_id = callback.from_user.id
    lang = get_user_language(user_id)
    settings = get_user_settings(user_id)
    
    new_status = not settings['notifications']
    update_user_settings(user_id, notifications=new_status)
    
    notif_status = get_text(lang, 'notifications_enabled') if new_status else get_text(lang, 'notifications_disabled')
    
    text = get_text(lang, 'settings',
                   notifications=notif_status,
                   time=settings['notification_time'],
                   language=settings['language'].upper())
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="🔔 " + ("OFF" if new_status else "ON"),
                callback_data="toggle_notifications"
            )
        ],
        [
            InlineKeyboardButton(text=get_text(lang, 'btn_language'), callback_data="change_language")
        ]
    ])
    
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()

@router.callback_query(F.data == 'change_language')
async def change_language_settings(callback: CallbackQuery):
    user_id = callback.from_user.id
    lang = get_user_language(user_id)
    text = get_text(lang, 'welcome', username=callback.from_user.first_name or "User")
    await callback.message.edit_text(text, reply_markup=get_language_keyboard())
    await callback.answer()

def register_handlers(dp):
    dp.include_router(router)
