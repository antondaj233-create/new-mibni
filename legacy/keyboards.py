from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def main_menu() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="🍽 Питание", callback_data="menu_nutrition")
    kb.button(text="💪 Тренировки", callback_data="menu_workouts")
    kb.button(text="👤 Профиль", callback_data="menu_profile")
    kb.adjust(1)
    return kb.as_markup()


def nutrition_menu() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="➕ Добавить блюдо", callback_data="nutrition_add")
    kb.button(text="📜 История", callback_data="nutrition_history")
    kb.button(text="📊 Статистика", callback_data="nutrition_stats")
    kb.button(text="⬅️ Назад", callback_data="menu_main")
    kb.adjust(1)
    return kb.as_markup()


def stats_period_menu() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="День", callback_data="stats_day")
    kb.button(text="Неделя", callback_data="stats_week")
    kb.button(text="Месяц", callback_data="stats_month")
    kb.button(text="Год", callback_data="stats_year")
    kb.button(text="⬅️ Назад", callback_data="menu_nutrition")
    kb.adjust(2, 2, 1)
    return kb.as_markup()


def profile_menu() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="⚖️ Единицы измерения", callback_data="profile_units")
    kb.button(text="🕐 Часовой пояс", callback_data="profile_timezone")
    kb.button(text="🎯 Дневная цель по калориям", callback_data="profile_goal")
    kb.button(text="⬅️ Назад", callback_data="menu_main")
    kb.adjust(1)
    return kb.as_markup()


def units_menu() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="Метрическая (кг)", callback_data="units_metric")
    kb.button(text="Имперская (фунты)", callback_data="units_imperial")
    kb.button(text="⬅️ Назад", callback_data="menu_profile")
    kb.adjust(1)
    return kb.as_markup()


def back_to_nutrition() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="⬅️ Назад", callback_data="menu_nutrition")
    return kb.as_markup()


def back_to_profile() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="⬅️ Назад", callback_data="menu_profile")
    return kb.as_markup()
