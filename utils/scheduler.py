import asyncio
from datetime import datetime
from config import FOCUS_TIME, BREAK_TIME
from translations import get_text

active_sessions = {}

async def start_focus_session(user_id, bot, lang):
    active_sessions[user_id] = {
        'start_time': datetime.now(),
        'phase': 'focus',
        'task': None,
        'lang': lang,
        'remaining': FOCUS_TIME
    }
    task = asyncio.create_task(focus_timer(user_id, bot, lang))
    active_sessions[user_id]['task'] = task

async def focus_timer(user_id, bot, lang):
    try:
        # Focus vaqti
        for minute in range(FOCUS_TIME, 0, -1):
            if user_id not in active_sessions:
                return
            active_sessions[user_id]['remaining'] = minute
            await asyncio.sleep(60)
        
        if user_id not in active_sessions:
            return
        
        await bot.send_message(user_id, get_text(lang, 'focus_ended'))
        active_sessions[user_id]['phase'] = 'break'
        active_sessions[user_id]['remaining'] = BREAK_TIME
        
        # Break vaqti
        for minute in range(BREAK_TIME, 0, -1):
            if user_id not in active_sessions:
                return
            active_sessions[user_id]['remaining'] = minute
            await asyncio.sleep(60)
        
        if user_id not in active_sessions:
            return
        
        await bot.send_message(user_id, get_text(lang, 'break_ended'))
        stop_focus_session(user_id)
        
    except asyncio.CancelledError:
        pass

def stop_focus_session(user_id):
    if user_id in active_sessions:
        task = active_sessions[user_id].get('task')
        if task and not task.done():
            task.cancel()
        del active_sessions[user_id]
