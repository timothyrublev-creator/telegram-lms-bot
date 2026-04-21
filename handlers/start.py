from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import random
import string
from database import add_user, get_user, is_admin
from keyboards import main_menu_keyboard, admin_menu_keyboard

router = Router()

class RegisterState(StatesGroup):
    waiting_for_name = State()
    waiting_for_photo = State()

def generate_promo_code():
    return "MASTER_" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    user_id = message.from_user.id
    user = get_user(user_id)
    
    # Разбор промокода из /start promo123
    args = message.text.split()
    referrer_promo = args[1] if len(args) > 1 else None
    
    if user:
        # Пользователь уже есть
        if is_admin(user_id):
            await message.answer("👋 Здравствуйте, руководитель!", reply_markup=admin_menu_keyboard())
        else:
            await message.answer(f"С возвращением, {user['name']}!", reply_markup=main_menu_keyboard())
    else:
        # Новая регистрация
        if referrer_promo:
            # Найти пригласившего
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute("SELECT user_id FROM users WHERE promo_code = ?", (referrer_promo,))
            referrer = cursor.fetchone()
            conn.close()
            await state.update_data(referrer_id=referrer['user_id'] if referrer else None)
        
        await message.answer("📝 Добро пожаловать! Как вас зовут?")
        await state.set_state(RegisterState.waiting_for_name)

@router.message(RegisterState.waiting_for_name)
async def register_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("📸 Теперь отправьте своё фото (аватар) — так руководитель будет знать вас в лицо\nИли нажмите /skip")
    await state.set_state(RegisterState.waiting_for_photo)

@router.message(RegisterState.waiting_for_photo, F.photo)
async def register_photo(message: Message, state: FSMContext):
    photo_file_id = message.photo[-1].file_id
    data = await state.get_data()
    
    user_id = message.from_user.id
    name = data['name']
    promo_code = generate_promo_code()
    referrer_id = data.get('referrer_id')
    
    add_user(user_id, name, promo_code, referrer_id, photo_file_id)
    
    # Бонус пригласившему
    if referrer_id:
        from referral import add_referral_bonus
        add_referral_bonus(referrer_id, user_id)
        await message.answer("🎉 Вы зарегистрированы по промокоду! Ваш друг получил бонус.")
    
    await message.answer(
        f"✅ Регистрация завершена!\n"
        f"Ваш промокод: `{promo_code}`\n"
        f"Дайте его друзьям — получите бонус на баланс.",
        parse_mode="Markdown",
        reply_markup=main_menu_keyboard()
    )
    await state.clear()

@router.message(Command("skip"), RegisterState.waiting_for_photo)
async def skip_photo(message: Message, state: FSMContext):
    data = await state.get_data()
    user_id = message.from_user.id
    add_user(user_id, data['name'], generate_promo_code(), data.get('referrer_id'))
    await message.answer("✅ Регистрация завершена без фото", reply_markup=main_menu_keyboard())
    await state.clear()