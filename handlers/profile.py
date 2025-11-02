from aiogram import Router, F
from aiogram.types import Message, FSInputFile
from database.db import (get_stats, get_tasks, get_user_language, 
                         get_achievements, get_weekly_stats)
from translations import get_text
import json
from datetime import datetime, timedelta

router = Router()

# Yutuqlar tarjimalari
ACHIEVEMENT_NAMES = {
    'uz': {
        'first_10': '🌟 Boshlang\'ich',
        'veteran_50': '⭐ Veteran',
        'master_100': '💎 Ustoz',
        'legend_500': '👑 Afsona',
        'week_streak': '🔥 Haftalik seriya',
        'month_streak': '🔥 Oylik seriya',
        'century_streak': '🔥 Yuzlik seriya'
    },
    'ru': {
        'first_10': '🌟 Начинающий',
        'veteran_50': '⭐ Ветеран',
        'master_100': '💎 Мастер',
        'legend_500': '👑 Легенда',
        'week_streak': '🔥 Недельная серия',
        'month_streak': '🔥 Месячная серия',
        'century_streak': '🔥 Вековая серия'
    },
    'en': {
        'first_10': '🌟 Beginner',
        'veteran_50': '⭐ Veteran',
        'master_100': '💎 Master',
        'legend_500': '👑 Legend',
        'week_streak': '🔥 Week Streak',
        'month_streak': '🔥 Month Streak',
        'century_streak': '🔥 Century Streak'
    }
}

ACHIEVEMENT_DESC = {
    'uz': {
        'first_10': '10 ta vazifa bajarildi',
        'veteran_50': '50 ta vazifa bajarildi',
        'master_100': '100 ta vazifa bajarildi',
        'legend_500': '500 ta vazifa bajarildi',
        'week_streak': '7 kun ketma-ket faol',
        'month_streak': '30 kun ketma-ket faol',
        'century_streak': '100 kun ketma-ket faol'
    },
    'ru': {
        'first_10': 'Выполнено 10 задач',
        'veteran_50': 'Выполнено 50 задач',
        'master_100': 'Выполнено 100 задач',
        'legend_500': 'Выполнено 500 задач',
        'week_streak': '7 дней подряд активны',
        'month_streak': '30 дней подряд активны',
        'century_streak': '100 дней подряд активны'
    },
    'en': {
        'first_10': 'Completed 10 tasks',
        'veteran_50': 'Completed 50 tasks',
        'master_100': 'Completed 100 tasks',
        'legend_500': 'Completed 500 tasks',
        'week_streak': '7 days active in a row',
        'month_streak': '30 days active in a row',
        'century_streak': '100 days active in a row'
    }
}

@router.message(F.text.in_(['👤 Profil', '👤 Профиль', '👤 Profile']))
async def btn_profile(message: Message):
    user_id = message.from_user.id
    lang = get_user_language(user_id)
    stats = get_stats(user_id)
    
    if stats['percentage'] >= 80:
        motivation = get_text(lang, 'motivation_high')
    elif stats['percentage'] >= 50:
        motivation = get_text(lang, 'motivation_medium')
    else:
        motivation = get_text(lang, 'motivation_low')
    
    text = get_text(lang, 'profile', 
                   total=stats['total'],
                   completed=stats['completed'],
                   pending=stats['pending'],
                   percentage=stats['percentage'],
                   categories=stats['categories'],
                   achievements=stats['achievements'],
                   streak=stats['streak'],
                   motivation=motivation)
    
    await message.answer(text)

@router.message(F.text.in_(['🏆 Yutuqlar', '🏆 Достижения', '🏆 Achievements']))
async def btn_achievements(message: Message):
    user_id = message.from_user.id
    lang = get_user_language(user_id)
    achievements = get_achievements(user_id)
    
    if not achievements:
        await message.answer(get_text(lang, 'achievements_title') + "\n📭 Hozircha yutuqlar yo'q")
        return
    
    text = get_text(lang, 'achievements_title')
    
    for ach_type, unlocked_at in achievements:
        name = ACHIEVEMENT_NAMES[lang].get(ach_type, ach_type)
        desc = ACHIEVEMENT_DESC[lang].get(ach_type, '')
        date = datetime.fromisoformat(unlocked_at).strftime('%d.%m.%Y')
        text += f"{name}\n<i>{desc}</i>\n🗓 {date}\n\n"
    
    await message.answer(text)

@router.message(F.text.in_(['📊 Haftalik hisobot', '📊 Недельный отчет', '📊 Weekly Report']))
async def btn_weekly_report(message: Message):
    user_id = message.from_user.id
    lang = get_user_language(user_id)
    stats = get_weekly_stats(user_id)
    
    today = datetime.now().date()
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)
    week_str = f"{week_start.strftime('%d.%m')} - {week_end.strftime('%d.%m.%Y')}"
    
    if stats['activity'] >= 70:
        motivation = get_text(lang, 'motivation_high')
    elif stats['activity'] >= 40:
        motivation = get_text(lang, 'motivation_medium')
    else:
        motivation = get_text(lang, 'motivation_low')
    
    text = get_text(lang, 'weekly_report',
                   week=week_str,
                   added=stats['added'],
                   completed=stats['completed'],
                   activity=stats['activity'],
                   motivation=motivation)
    
    await message.answer(text)

@router.message(F.text.in_(['📁 Eksport', '📁 Экспорт', '📁 Export']))
async def btn_export(message: Message):
    user_id = message.from_user.id
    lang = get_user_language(user_id)
    tasks = get_tasks(user_id)
    
    if not tasks:
        await message.answer(get_text(lang, 'no_tasks_export'))
        return
    
    export_data = {
        'user_id': user_id,
        'export_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'tasks': []
    }
    
    for task in tasks:
        task_id, text, category, status, created_at = task
        export_data['tasks'].append({
            'id': task_id,
            'text': text,
            'category': category,
            'status': status,
            'created_at': created_at
        })
    
    filename = f"tasks_{user_id}_{datetime.now().strftime('%Y%m%d')}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, ensure_ascii=False, indent=2)
    
    file = FSInputFile(filename)
    caption = get_text(lang, 'export_caption', date=export_data['export_date'])
    await message.answer_document(document=file, caption=caption)
    
    import os
    os.remove(filename)

def register_handlers(dp):
    dp.include_router(router)
