from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from sqlalchemy import select

from database.db import async_session
from database.models import User
from keyboards import back_to_profile, profile_menu, units_menu

router = Router()


class ProfileStates(StatesGroup):
    waiting_timezone = State()
    waiting_goal = State()


async def get_user(telegram_id: int) -> User:
    async with async_session() as session:
        result = await session.execute(select(User).where(User.telegram_id == telegram_id))
        return result.scalar_one()


@router.callback_query(F.data == "menu_profile")
async def open_profile(callback: CallbackQuery) -> None:
    user = await get_user(callback.from_user.id)
    units_label = "кг (метрическая)" if user.units == "metric" else "фунты (имперская)"
    goal_label = f"{user.daily_calorie_goal} ккал" if user.daily_calorie_goal else "не задана"

    text = (
        "👤 Профиль\n\n"
        f"⚖️ Единицы измерения: {units_label}\n"
        f"🕐 Часовой пояс: {user.timezone}\n"
        f"🎯 Дневная цель: {goal_label}"
    )
    await callback.message.edit_text(text, reply_markup=profile_menu())
    await callback.answer()


# --- Единицы измерения ---

@router.callback_query(F.data == "profile_units")
async def choose_units(callback: CallbackQuery) -> None:
    await callback.message.edit_text("Выбери единицы измерения:", reply_markup=units_menu())
    await callback.answer()


@router.callback_query(F.data.in_(["units_metric", "units_imperial"]))
async def set_units(callback: CallbackQuery) -> None:
    units = "metric" if callback.data == "units_metric" else "imperial"
    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == callback.from_user.id)
        )
        user = result.scalar_one()
        user.units = units
        await session.commit()

    await callback.answer("Единицы измерения обновлены ✅")
    await open_profile(callback)


# --- Часовой пояс ---

@router.callback_query(F.data == "profile_timezone")
async def ask_timezone(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(ProfileStates.waiting_timezone)
    await callback.message.edit_text(
        "Введи свой часовой пояс в формате IANA, например:\n"
        "Europe/Moscow, Europe/Kyiv, Asia/Almaty",
        reply_markup=back_to_profile(),
    )
    await callback.answer()


@router.message(ProfileStates.waiting_timezone)
async def save_timezone(message: Message, state: FSMContext) -> None:
    timezone_str = message.text.strip()

    # Простая проверка валидности через zoneinfo
    try:
        from zoneinfo import ZoneInfo

        ZoneInfo(timezone_str)
    except Exception:
        await message.answer(
            "Не удалось распознать часовой пояс. Пример правильного формата: Europe/Moscow"
        )
        return

    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == message.from_user.id)
        )
        user = result.scalar_one()
        user.timezone = timezone_str
        await session.commit()

    await state.clear()
    await message.answer(f"Часовой пояс обновлён: {timezone_str} ✅", reply_markup=back_to_profile())


# --- Дневная цель по калориям ---

@router.callback_query(F.data == "profile_goal")
async def ask_goal(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(ProfileStates.waiting_goal)
    await callback.message.edit_text(
        "Введи свою дневную цель по калориям (число, например 2200):",
        reply_markup=back_to_profile(),
    )
    await callback.answer()


@router.message(ProfileStates.waiting_goal)
async def save_goal(message: Message, state: FSMContext) -> None:
    try:
        goal = int(message.text.strip())
        if goal <= 0:
            raise ValueError
    except ValueError:
        await message.answer("Введи целое положительное число, например 2200.")
        return

    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == message.from_user.id)
        )
        user = result.scalar_one()
        user.daily_calorie_goal = goal
        await session.commit()

    await state.clear()
    await message.answer(f"Дневная цель обновлена: {goal} ккал ✅", reply_markup=back_to_profile())
