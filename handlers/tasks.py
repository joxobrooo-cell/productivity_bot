from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database.db import (add_task, get_tasks, mark_done, delete_task, 
                         get_user_language, get_task_by_id)
from translations import get_text
from utils.keyboards import (get_category_keyboard, get_task_actions_keyboard,
                            get_confirm_keyboard, get_main_keyboard)

router = Router()

class TaskStates(StatesGroup):
    waiting_for_task_text = State()
    waiting_for_category = State()

@router.message(F.text.in_(['➕ Vazifa qo\'shish', '➕ Добавить задачу', '➕ Add Task']))
async def btn_add_task(message: Message, state: FSMContext):
    user_id = message.from_user.id
    lang = get_user_language(user_id)
    await message.answer(get_text(lang, 'add_task_prompt'))
    await state.set_state(TaskStates.waiting_for_task_text)

@router.message(TaskStates.waiting_for_task_text)
async def process_task_text(message: Message, state: FSMContext):
    user_id = message.from_user.id
    lang = get_user_language(user_id)
    
    await state.update_data(task_text=message.text)
    await message.answer(
        get_text(lang, 'select_category'),
        reply_markup=get_category_keyboard(lang)
    )
    await state.set_state(TaskStates.waiting_for_category)

@router.callback_query(F.data.startswith('cat_'))
async def process_category_selection(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    lang = get_user_language(user_id)
    
    category = callback.data.split('_')[1]
    data = await state.get_data()
    task_text = data.get('task_text')
    
    if task_text:
        task_id = add_task(user_id, task_text, category)
        if task_id:
            category_name = get_text(lang, f'cat_{category}')
            await callback.message.edit_text(
                get_text(lang, 'task_added', text=task_text, category=category_name, task_id=task_id)
            )
        else:
            await callback.message.edit_text(get_text(lang, 'task_add_error'))
    
    await state.clear()
    await callback.answer()

@router.callback_query(F.data == 'cancel_add')
async def cancel_add_task(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    lang = get_user_language(user_id)
    await state.clear()
    await callback.message.edit_text(get_text(lang, 'task_add_cancelled'))
    await callback.answer()

@router.message(F.text.in_(['📋 Vazifalarim', '📋 Мои задачи', '📋 My Tasks']))
async def btn_my_tasks(message: Message):
    user_id = message.from_user.id
    lang = get_user_language(user_id)
    tasks = get_tasks(user_id)
    
    if not tasks:
        await message.answer(get_text(lang, 'no_tasks'))
        return
    
    pending_tasks = []
    completed_tasks = []
    
    for task in tasks:
        task_id, text, category, status, created_at = task
        emoji = "✅" if status == "completed" else "⏳"
        cat_emoji = get_text(lang, f'cat_{category}').split()[0]
        task_text = f"{emoji} <b>#{task_id}</b> {cat_emoji} {text}"
        
        if status == "completed":
            completed_tasks.append(task_text)
        else:
            pending_tasks.append(task_text)
    
    result = f"<b>{get_text(lang, 'your_tasks')}</b>\n\n"
    
    if pending_tasks:
        result += f"<b>{get_text(lang, 'pending')}</b>\n" + "\n".join(pending_tasks[:10]) + "\n\n"
    
    if completed_tasks:
        result += f"<b>{get_text(lang, 'completed')}</b>\n" + "\n".join(completed_tasks[:5])
    
    result += get_text(lang, 'select_task_action')
    
    # Inline tugmalar - faqat bajarilmagan vazifalar uchun
    if pending_tasks:
        # Birinchi vazifa uchun tugmalar
        first_pending = [t for t in tasks if t[3] == 'pending'][0]
        await message.answer(
            result,
            reply_markup=get_task_actions_keyboard(first_pending[0], lang)
        )
    else:
        await message.answer(result)

@router.callback_query(F.data.startswith('complete_'))
async def process_complete_task(callback: CallbackQuery):
    user_id = callback.from_user.id
    lang = get_user_language(user_id)
    task_id = int(callback.data.split('_')[1])
    
    task = get_task_by_id(task_id, user_id)
    if task and mark_done(task_id, user_id):
        await callback.message.edit_text(
            get_text(lang, 'task_completed', text=task[1])
        )
    else:
        await callback.message.edit_text(get_text(lang, 'task_not_found'))
    
    await callback.answer()

@router.callback_query(F.data.startswith('delete_'))
async def process_delete_request(callback: CallbackQuery):
    user_id = callback.from_user.id
    lang = get_user_language(user_id)
    task_id = int(callback.data.split('_')[1])
    
    task = get_task_by_id(task_id, user_id)
    if task:
        await callback.message.edit_text(
            get_text(lang, 'confirm_delete', text=task[1]),
            reply_markup=get_confirm_keyboard('delete', task_id, lang)
        )
    else:
        await callback.message.edit_text(get_text(lang, 'task_not_found'))
    
    await callback.answer()

@router.callback_query(F.data.startswith('confirm_delete_'))
async def process_confirm_delete(callback: CallbackQuery):
    user_id = callback.from_user.id
    lang = get_user_language(user_id)
    task_id = int(callback.data.split('_')[2])
    
    task = get_task_by_id(task_id, user_id)
    if task and delete_task(task_id, user_id):
        await callback.message.edit_text(
            get_text(lang, 'task_deleted', text=task[1])
        )
    else:
        await callback.message.edit_text(get_text(lang, 'task_not_found'))
    
    await callback.answer()

@router.callback_query(F.data == 'cancel')
async def process_cancel(callback: CallbackQuery):
    await callback.message.delete()
    await callback.answer()

def register_handlers(dp):
    dp.include_router(router)
