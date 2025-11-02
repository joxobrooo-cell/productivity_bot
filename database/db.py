import sqlite3
import logging
from config import DB_PATH
from datetime import datetime, timedelta

def get_connection():
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Foydalanuvchilar jadvali
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE,
            username TEXT,
            language TEXT DEFAULT 'uz',
            notifications BOOLEAN DEFAULT 1,
            notification_time TEXT DEFAULT '09:00',
            streak INTEGER DEFAULT 0,
            last_activity DATE,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Vazifalar jadvali
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            text TEXT,
            category TEXT DEFAULT 'other',
            status TEXT DEFAULT 'pending',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            completed_at DATETIME
        )
    """)
    
    # Yutuqlar jadvali
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS achievements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            achievement_type TEXT,
            unlocked_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Haftalik statistika
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS weekly_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            week_start DATE,
            tasks_added INTEGER DEFAULT 0,
            tasks_completed INTEGER DEFAULT 0,
            focus_sessions INTEGER DEFAULT 0
        )
    """)
    
    conn.commit()
    conn.close()
    logging.info("Ma'lumotlar bazasi tayyor")

def add_user(user_id, username):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)", (user_id, username))
        conn.commit()
    except Exception as e:
        logging.error(f"Foydalanuvchi qo'shishda xato: {e}")
    finally:
        conn.close()

def get_user_language(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT language FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else 'uz'

def set_user_language(user_id, language):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE users SET language = ? WHERE user_id = ?", (language, user_id))
        conn.commit()
        return True
    except Exception as e:
        logging.error(f"Tilni o'zgartirishda xato: {e}")
        return False
    finally:
        conn.close()

def add_task(user_id, text, category='other'):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO tasks (user_id, text, category) VALUES (?, ?, ?)", (user_id, text, category))
        conn.commit()
        task_id = cursor.lastrowid
        
        # Haftalik statistikani yangilash
        update_weekly_stats(user_id, 'added')
        
        # Yutuqlarni tekshirish
        check_achievements(user_id, 'task_added')
        
        logging.info(f"Vazifa qo'shildi: {user_id} - {text}")
        return task_id
    except Exception as e:
        logging.error(f"Vazifa qo'shishda xato: {e}")
        return None
    finally:
        conn.close()

def get_tasks(user_id, status=None, category=None):
    conn = get_connection()
    cursor = conn.cursor()
    
    query = "SELECT id, text, category, status, created_at FROM tasks WHERE user_id = ?"
    params = [user_id]
    
    if status:
        query += " AND status = ?"
        params.append(status)
    
    if category:
        query += " AND category = ?"
        params.append(category)
    
    query += " ORDER BY created_at DESC"
    
    cursor.execute(query, params)
    tasks = cursor.fetchall()
    conn.close()
    return tasks

def get_task_by_id(task_id, user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, text, category, status FROM tasks WHERE id = ? AND user_id = ?", (task_id, user_id))
    task = cursor.fetchone()
    conn.close()
    return task

def mark_done(task_id, user_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE tasks SET status = 'completed', completed_at = ? WHERE id = ? AND user_id = ?", 
                      (datetime.now(), task_id, user_id))
        conn.commit()
        success = cursor.rowcount > 0
        
        if success:
            # Streak yangilash
            update_streak(user_id)
            
            # Haftalik statistikani yangilash
            update_weekly_stats(user_id, 'completed')
            
            # Yutuqlarni tekshirish
            check_achievements(user_id, 'task_completed')
            
            logging.info(f"Vazifa bajarildi: {task_id}")
        
        return success
    except Exception as e:
        logging.error(f"Vazifani belgilashda xato: {e}")
        return False
    finally:
        conn.close()

def delete_task(task_id, user_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM tasks WHERE id = ? AND user_id = ?", (task_id, user_id))
        conn.commit()
        success = cursor.rowcount > 0
        logging.info(f"Vazifa o'chirildi: {task_id}")
        return success
    except Exception as e:
        logging.error(f"Vazifani o'chirishda xato: {e}")
        return False
    finally:
        conn.close()

def get_stats(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM tasks WHERE user_id = ?", (user_id,))
    total = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM tasks WHERE user_id = ? AND status = 'completed'", (user_id,))
    completed = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(DISTINCT category) FROM tasks WHERE user_id = ?", (user_id,))
    categories = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM achievements WHERE user_id = ?", (user_id,))
    achievements = cursor.fetchone()[0]
    
    cursor.execute("SELECT streak FROM users WHERE user_id = ?", (user_id,))
    streak_result = cursor.fetchone()
    streak = streak_result[0] if streak_result else 0
    
    conn.close()
    
    percentage = (completed / total * 100) if total > 0 else 0
    return {
        'total': total,
        'completed': completed,
        'pending': total - completed,
        'percentage': round(percentage, 1),
        'categories': categories,
        'achievements': achievements,
        'streak': streak
    }

def update_streak(user_id):
    """Kunlik seriyani yangilash"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT last_activity, streak FROM users WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()
        
        today = datetime.now().date()
        
        if result:
            last_activity = datetime.strptime(result[0], '%Y-%m-%d').date() if result[0] else None
            current_streak = result[1] or 0
            
            if last_activity:
                days_diff = (today - last_activity).days
                
                if days_diff == 0:
                    # Bugun allaqachon faol
                    pass
                elif days_diff == 1:
                    # Seriya davom etmoqda
                    current_streak += 1
                    cursor.execute("UPDATE users SET streak = ?, last_activity = ? WHERE user_id = ?", 
                                 (current_streak, today, user_id))
                else:
                    # Seriya uzildi
                    cursor.execute("UPDATE users SET streak = 1, last_activity = ? WHERE user_id = ?", 
                                 (today, user_id))
            else:
                cursor.execute("UPDATE users SET streak = 1, last_activity = ? WHERE user_id = ?", 
                             (today, user_id))
        
        conn.commit()
    except Exception as e:
        logging.error(f"Streak yangilashda xato: {e}")
    finally:
        conn.close()

def check_achievements(user_id, action):
    """Yutuqlarni tekshirish va berish"""
    conn = get_connection()
    cursor = conn.cursor()
    
    new_achievements = []
    
    try:
        # Vazifalar soni bo'yicha yutuqlar
        cursor.execute("SELECT COUNT(*) FROM tasks WHERE user_id = ? AND status = 'completed'", (user_id,))
        completed_count = cursor.fetchone()[0]
        
        achievements_map = {
            10: 'first_10',
            50: 'veteran_50',
            100: 'master_100',
            500: 'legend_500'
        }
        
        for count, ach_type in achievements_map.items():
            if completed_count >= count:
                # Yutuq allaqachon bormi?
                cursor.execute("SELECT id FROM achievements WHERE user_id = ? AND achievement_type = ?", 
                             (user_id, ach_type))
                if not cursor.fetchone():
                    cursor.execute("INSERT INTO achievements (user_id, achievement_type) VALUES (?, ?)", 
                                 (user_id, ach_type))
                    new_achievements.append(ach_type)
        
        # Streak bo'yicha yutuqlar
        cursor.execute("SELECT streak FROM users WHERE user_id = ?", (user_id,))
        streak = cursor.fetchone()[0] or 0
        
        streak_achievements = {
            7: 'week_streak',
            30: 'month_streak',
            100: 'century_streak'
        }
        
        for days, ach_type in streak_achievements.items():
            if streak >= days:
                cursor.execute("SELECT id FROM achievements WHERE user_id = ? AND achievement_type = ?", 
                             (user_id, ach_type))
                if not cursor.fetchone():
                    cursor.execute("INSERT INTO achievements (user_id, achievement_type) VALUES (?, ?)", 
                                 (user_id, ach_type))
                    new_achievements.append(ach_type)
        
        conn.commit()
        return new_achievements
    except Exception as e:
        logging.error(f"Yutuqlarni tekshirishda xato: {e}")
        return []
    finally:
        conn.close()

def get_achievements(user_id):
    """Foydalanuvchi yutuqlarini olish"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT achievement_type, unlocked_at FROM achievements WHERE user_id = ? ORDER BY unlocked_at DESC", 
                  (user_id,))
    achievements = cursor.fetchall()
    conn.close()
    return achievements

def update_weekly_stats(user_id, stat_type):
    """Haftalik statistikani yangilash"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        today = datetime.now().date()
        week_start = today - timedelta(days=today.weekday())
        
        cursor.execute("SELECT id FROM weekly_stats WHERE user_id = ? AND week_start = ?", 
                      (user_id, week_start))
        
        if cursor.fetchone():
            if stat_type == 'added':
                cursor.execute("UPDATE weekly_stats SET tasks_added = tasks_added + 1 WHERE user_id = ? AND week_start = ?", 
                             (user_id, week_start))
            elif stat_type == 'completed':
                cursor.execute("UPDATE weekly_stats SET tasks_completed = tasks_completed + 1 WHERE user_id = ? AND week_start = ?", 
                             (user_id, week_start))
            elif stat_type == 'focus':
                cursor.execute("UPDATE weekly_stats SET focus_sessions = focus_sessions + 1 WHERE user_id = ? AND week_start = ?", 
                             (user_id, week_start))
        else:
            values = {'added': (1, 0, 0), 'completed': (0, 1, 0), 'focus': (0, 0, 1)}
            added, completed, focus = values.get(stat_type, (0, 0, 0))
            cursor.execute("""
                INSERT INTO weekly_stats (user_id, week_start, tasks_added, tasks_completed, focus_sessions) 
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, week_start, added, completed, focus))
        
        conn.commit()
    except Exception as e:
        logging.error(f"Haftalik statistika yangilashda xato: {e}")
    finally:
        conn.close()

def get_weekly_stats(user_id):
    """Haftalik statistikani olish"""
    conn = get_connection()
    cursor = conn.cursor()
    today = datetime.now().date()
    week_start = today - timedelta(days=today.weekday())
    
    cursor.execute("""
        SELECT tasks_added, tasks_completed, focus_sessions 
        FROM weekly_stats 
        WHERE user_id = ? AND week_start = ?
    """, (user_id, week_start))
    
    result = cursor.fetchone()
    conn.close()
    
    if result:
        added, completed, focus = result
        activity = (completed / added * 100) if added > 0 else 0
        return {
            'added': added,
            'completed': completed,
            'focus_sessions': focus,
            'activity': round(activity, 1)
        }
    return {'added': 0, 'completed': 0, 'focus_sessions': 0, 'activity': 0}

def get_user_settings(user_id):
    """Foydalanuvchi sozlamalarini olish"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT language, notifications, notification_time FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return {
            'language': result[0],
            'notifications': result[1],
            'notification_time': result[2]
        }
    return {'language': 'uz', 'notifications': True, 'notification_time': '09:00'}

def update_user_settings(user_id, notifications=None, notification_time=None):
    """Sozlamalarni yangilash"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        if notifications is not None:
            cursor.execute("UPDATE users SET notifications = ? WHERE user_id = ?", (notifications, user_id))
        if notification_time:
            cursor.execute("UPDATE users SET notification_time = ? WHERE user_id = ?", (notification_time, user_id))
        conn.commit()
        return True
    except Exception as e:
        logging.error(f"Sozlamalarni yangilashda xato: {e}")
        return False
    finally:
        conn.close()
