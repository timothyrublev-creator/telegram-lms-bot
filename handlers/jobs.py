from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database import (
    get_db, get_user, is_admin, create_job, get_open_jobs, 
    get_user_jobs, take_job, complete_job, confirm_job_payment
)
from keyboards import back_button

router = Router()

class CreateJobState(StatesGroup):
    waiting_for_title = State()
    waiting_for_description = State()
    waiting_for_address = State()
    waiting_for_payment = State()

# ========== МАСТЕР: Список заказов ==========
@router.callback_query(F.data == "jobs_list")
async def show_open_jobs(callback: CallbackQuery):
    jobs = get_open_jobs()
    if not jobs:
        await callback.message.edit_text("📭 Сейчас нет открытых заказов.", reply_markup=back_button())
        return
    
    for job in jobs:
        text = (
            f"🔧 **{job['title']}**\n"
            f"📝 {job['description']}\n"
            f"📍 {job['address']}\n"
            f"💰 {job['payment']} ₽\n"
        )
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ Взять заказ", callback_data=f"take_job_{job['id']}")],
            [InlineKeyboardButton(text="◀ Назад", callback_data="main_menu")]
        ])
        await callback.message.answer(text, parse_mode="Markdown", reply_markup=kb)
    await callback.answer()

@router.callback_query(F.data.startswith("take_job_"))
async def take_job_handler(callback: CallbackQuery):
    job_id = int(callback.data.split("_")[2])
    user_id = callback.from_user.id
    
    result = take_job(job_id, user_id)
    if result:
        await callback.message.edit_text("✅ Вы взяли заказ. После выполнения нажмите «Завершить» в разделе «Мои заказы».")
    else:
        await callback.message.edit_text("❌ Заказ уже кто-то взял.", reply_markup=back_button())
    await callback.answer()

# ========== МАСТЕР: Мои заказы ==========
@router.callback_query(F.data == "my_jobs")
async def show_my_jobs(callback: CallbackQuery):
    user_id = callback.from_user.id
    jobs = get_user_jobs(user_id)
    
    if not jobs:
        await callback.message.edit_text("📭 У вас нет активных заказов.", reply_markup=back_button())
        return
    
    for job in jobs:
        text = (
            f"🔧 **{job['title']}**\n"
            f"📍 {job['address']}\n"
            f"💰 {job['payment']} ₽\n"
            f"Статус: {job['status']}\n"
        )
        kb = InlineKeyboardMarkup(inline_keyboard=[])
        if job['status'] == 'taken':
            kb.inline_keyboard.append([InlineKeyboardButton(text="✅ Завершить", callback_data=f"complete_job_{job['id']}")])
        kb.inline_keyboard.append([InlineKeyboardButton(text="◀ Назад", callback_data="main_menu")])
        await callback.message.answer(text, parse_mode="Markdown", reply_markup=kb)
    await callback.answer()

@router.callback_query(F.data.startswith("complete_job_"))
async def complete_job_handler(callback: CallbackQuery):
    job_id = int(callback.data.split("_")[2])
    complete_job(job_id)
    await callback.message.edit_text("✅ Заказ выполнен. Ожидайте подтверждения от руководителя.")
    await callback.answer()

# ========== АДМИН: Создание заказа ==========
@router.callback_query(F.data == "admin_create_job")
async def admin_create_job_start(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("Нет прав")
        return
    await callback.message.edit_text("Введите название заказа:")
    await state.set_state(CreateJobState.waiting_for_title)
    await callback.answer()

@router.message(CreateJobState.waiting_for_title)
async def create_job_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text)
    await message.answer("Введите описание заказа:")
    await state.set_state(CreateJobState.waiting_for_description)

@router.message(CreateJobState.waiting_for_description)
async def create_job_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer("Введите адрес объекта:")
    await state.set_state(CreateJobState.waiting_for_address)

@router.message(CreateJobState.waiting_for_address)
async def create_job_address(message: Message, state: FSMContext):
    await state.update_data(address=message.text)
    await message.answer("Введите сумму оплаты (в рублях):")
    await state.set_state(CreateJobState.waiting_for_payment)

@router.message(CreateJobState.waiting_for_payment)
async def create_job_payment(message: Message, state: FSMContext):
    try:
        payment = int(message.text)
        data = await state.get_data()
        create_job(data['title'], data['description'], data['address'], payment, message.from_user.id)
        await message.answer("✅ Заказ создан! Мастера увидят его в разделе «Заказы рядом».")
        await state.clear()
    except ValueError:
        await message.answer("Введите число, например: 2000")

# ========== АДМИН: Подтверждение оплаты заказа ==========
@router.callback_query(F.data == "admin_complete_jobs")
async def admin_complete_jobs_list(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("Нет прав")
        return
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM jobs WHERE status = 'completed'")
    jobs = cursor.fetchall()
    conn.close()
    
    for job in jobs:
        text = f"🔧 {job['title']}\n💰 {job['payment']} ₽\nМастер ID: {job['taken_by']}"
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ Подтвердить оплату", callback_data=f"pay_job_{job['id']}")]
        ])
        await callback.message.answer(text, reply_markup=kb)
    await callback.answer()

@router.callback_query(F.data.startswith("pay_job_"))
async def pay_job_handler(callback: CallbackQuery):
    job_id = int(callback.data.split("_")[2])
    confirm_job_payment(job_id)
    await callback.message.edit_text("✅ Оплата подтверждена, деньги зачислены на баланс мастера.")
    await callback.answer()