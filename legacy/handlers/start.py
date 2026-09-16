from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, Message
from sqlalchemy import select

from database.db import async_session
from database.models import User
from keyboards import main_menu

router = Router()


@router.message(CommandStart())
async def start(message: Message) -> None:
    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == message.from_user.id)
        )
        user = result.scalar_one_or_none()
        if user is None:
            user = User(telegram_id=message.from_user.id)
            session.add(user)
            await session.commit()

    await message.answer(
        "Привет! Я твой фитнес-бот 💪\nВыбери раздел:",
        reply_markup=main_menu(),
    )


@router.callback_query(F.data == "menu_main")
async def back_to_main(callback: CallbackQuery) -> None:
    await callback.message.edit_text("Главное меню:", reply_markup=main_menu())
    await callback.answer()


@router.callback_query(F.data == "menu_workouts")
async def workouts_placeholder(callback: CallbackQuery) -> None:
    # Раздел тренировок будет реализован следующим этапом
    await callback.answer("Раздел тренировок в разработке 🛠", show_alert=True)
