from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Главное меню для обычного мастера
def main_menu_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📚 Мои уроки", callback_data="materials")],
        [InlineKeyboardButton(text="🎲 Слово дня (+10 баллов)", callback_data="daily_word")],
        [InlineKeyboardButton(text="⚡ Быстрая игра", callback_data="quick_quiz")],
        [InlineKeyboardButton(text="💰 Заказы рядом", callback_data="jobs_list")],
        [InlineKeyboardButton(text="🤖 Спросить эксперта", callback_data="ask_expert")],
        [InlineKeyboardButton(text="📊 Мой профиль", callback_data="my_profile")],
        [InlineKeyboardButton(text="👥 Пригласить друга", callback_data="referral")],
    ])

# Главное меню для админа/руководителя
def admin_menu_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📚 Управление уроками", callback_data="admin_lessons")],
        [InlineKeyboardButton(text="➕ Создать заказ", callback_data="admin_create_job")],
        [InlineKeyboardButton(text="👥 Все мастера", callback_data="admin_masters_list")],
        [InlineKeyboardButton(text="📈 Статистика", callback_data="admin_stats")],
        [InlineKeyboardButton(text="💰 Подтвердить оплаты", callback_data="admin_payments")],
        [InlineKeyboardButton(text="⚠️ Ошибки в уроках", callback_data="admin_feedback")],
        [InlineKeyboardButton(text="📎 Выгрузить отчёт Excel", callback_data="admin_export")],
    ])

# Кнопка "Назад" для всех
def back_button(callback_data: str = "main_menu"):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀ Назад", callback_data=callback_data)]
    ])
