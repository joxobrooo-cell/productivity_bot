from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from translations import get_text

def get_main_keyboard(lang='uz'):
    """Asosiy menyu keyboardi"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=get_text(lang, 'btn_add_task')),
                KeyboardButton(text=get_text(lang, 'btn_my_tasks'))
            ],
            [
                KeyboardButton(text=get_text(lang, 'btn_focus')),
                KeyboardButton(text=get_text(lang, 'btn_profile'))
            ],
            [
                KeyboardButton(text=get_text(lang, 'btn_achievements')),
                KeyboardButton(text=get_text(lang, 'btn_weekly_report'))
            ],
            [
                KeyboardButton(text=get_text(lang, 'btn_settings')),
                KeyboardButton(text=get_text(lang, 'btn_help'))
            ]
        ],
        resize_keyboard=True
    )
    return keyboard

def get_language_keyboard():
    """Til tanlash inline keyboardi"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🇺🇿 O'zbekcha", callback_data="lang_uz"),
            InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru")
        ],
        [
            InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en")
        ]
    ])
    return keyboard

def get_category_keyboard(lang='uz'):
    """Kategoriya tanlash inline keyboardi"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=get_text(lang, 'cat_work'), callback_data="cat_work"),
            InlineKeyboardButton(text=get_text(lang, 'cat_personal'), callback_data="cat_personal")
        ],
        [
            InlineKeyboardButton(text=get_text(lang, 'cat_study'), callback_data="cat_study"),
            InlineKeyboardButton(text=get_text(lang, 'cat_health'), callback_data="cat_health")
        ],
        [
            InlineKeyboardButton(text=get_text(lang, 'cat_hobby'), callback_data="cat_hobby"),
            InlineKeyboardButton(text=get_text(lang, 'cat_other'), callback_data="cat_other")
        ],
        [
            InlineKeyboardButton(text=get_text(lang, 'btn_cancel'), callback_data="cancel_add")
        ]
    ])
    return keyboard

def get_task_actions_keyboard(task_id, lang='uz'):
    """Vazifa amallar keyboardi"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=get_text(lang, 'btn_complete'), callback_data=f"complete_{task_id}"),
            InlineKeyboardButton(text=get_text(lang, 'btn_delete'), callback_data=f"delete_{task_id}")
        ]
    ])
    return keyboard

def get_confirm_keyboard(action, task_id, lang='uz'):
    """Tasdiqlash keyboardi"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=get_text(lang, 'btn_confirm'), callback_data=f"confirm_{action}_{task_id}"),
            InlineKeyboardButton(text=get_text(lang, 'btn_cancel'), callback_data="cancel")
        ]
    ])
    return keyboard

def get_focus_keyboard(lang='uz'):
    """Fokus rejim keyboardi"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=get_text(lang, 'btn_stop_focus'), callback_data="stop_focus")
        ]
    ])
    return keyboard

def get_back_keyboard(lang='uz'):
    """Orqaga qaytish keyboardi"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=get_text(lang, 'btn_back'))]
        ],
        resize_keyboard=True
    )
    return keyboard
