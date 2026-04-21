import aiohttp
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from config import DEEPSEEK_API_KEY, DEEPSEEK_API_URL, AI_ROLES
from database import log_ai_chat

router = Router()

@router.callback_query(F.data == "ask_expert")
async def ask_expert_menu(callback: CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⚡ Электрик", callback_data="expert_electrician")],
        [InlineKeyboardButton(text="🔧 Сантехник", callback_data="expert_plumber")],
        [InlineKeyboardButton(text="◀ Назад", callback_data="main_menu")]
    ])
    await callback.message.edit_text("Выберите специалиста:", reply_markup=kb)
    await callback.answer()

@router.callback_query(F.data.startswith("expert_"))
async def expert_chat_start(callback: CallbackQuery, state):
    role = "electrician" if "electrician" in callback.data else "plumber"
    await state.update_data(ai_role=role)
    await callback.message.edit_text(
        f"🤖 Вы выбрали {AI_ROLES[role].split()[1]}\n\nЗадайте ваш вопрос. Я отвечу как профессионал.\n\n(Для выхода отправьте /cancel)"
    )
    await callback.answer()

@router.message(F.text)
async def expert_chat_handler(message: Message, state):
    data = await state.get_data()
    role = data.get("ai_role")
    if not role:
        return
    
    if message.text == "/cancel":
        await state.clear()
        await message.answer("Выход из режима эксперта.", reply_markup=main_menu_keyboard())
        return
    
    async with aiohttp.ClientSession() as session:
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": AI_ROLES[role]},
                {"role": "user", "content": message.text}
            ]
        }
        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }
        async with session.post(DEEPSEEK_API_URL, json=payload, headers=headers) as resp:
            if resp.status == 200:
                result = await resp.json()
                answer = result["choices"][0]["message"]["content"]
                log_ai_chat(message.from_user.id, role, message.text, answer)
                await message.answer(answer[:4000])
            else:
                await message.answer("❌ Ошибка API. Попробуйте позже.")