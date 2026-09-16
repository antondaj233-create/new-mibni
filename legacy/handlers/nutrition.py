import io
from datetime import datetime, timedelta

from aiogram import F, Router, Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from sqlalchemy import func, select

# Импортируем обе функции из нашего ИИ модуля
from ai_nutrition import NutritionEstimationError, estimate_meal, estimate_meal_from_photo
from database.db import async_session
from database.models import Meal, User
from keyboards import back_to_nutrition, nutrition_menu, stats_period_menu

router = Router()


class NutritionStates(StatesGroup):
    waiting_meal_description = State()


async def get_user(telegram_id: int) -> User:
    async with async_session() as session:
        result = await session.execute(select(User).where(User.telegram_id == telegram_id))
        return result.scalar_one()


@router.callback_query(F.data == "menu_nutrition")
async def open_nutrition(callback: CallbackQuery) -> None:
    await callback.message.edit_text("🍽 Питание:", reply_markup=nutrition_menu())
    await callback.answer()


# --- Добавление блюда через ИИ ---

@router.callback_query(F.data == "nutrition_add")
async def ask_meal(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(NutritionStates.waiting_meal_description)
    await callback.message.edit_text(
        "Опиши, что ты съел — можно одним сообщением, например:\n"
        "«овсянка 150г с бананом и ложкой мёда»\n\n"
        "Либо ты можешь просто **скинуть мне фотографию своего блюда** прямо в чат, и я определю его КБЖУ!",
        reply_markup=back_to_nutrition(),
    )
    await callback.answer()


@router.message(NutritionStates.waiting_meal_description, F.text)
async def save_meal(message: Message, state: FSMContext) -> None:
    description = message.text.strip()
    thinking_msg = await message.answer("Считаю КБЖУ... 🧮")

    try:
        estimation = await estimate_meal(description)
    except NutritionEstimationError:
        await thinking_msg.edit_text(
            "Не получилось оценить это блюдо. Попробуй описать его чуть подробнее "
            "(например, укажи примерный вес порции)."
        )
        return

    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == message.from_user.id)
        )
        user = result.scalar_one()

        meal = Meal(
            user_id=user.id,
            text_description=description,
            calories=estimation["calories"],
            protein=estimation["protein"],
            fat=estimation["fat"],
            carbs=estimation["carbs"],
        )
        session.add(meal)
        await session.commit()

    await state.clear()
    await thinking_msg.edit_text(
        "Записал ✅\n\n"
        f"«{description}»\n"
        f"🔥 Калории: {estimation['calories']:.0f} ккал\n"
        f"🥩 Белки: {estimation['protein']:.1f} г\n"
        f"🧈 Жиры: {estimation['fat']:.1f} г\n"
        f"🍞 Углеводы: {estimation['carbs']:.1f} г",
        reply_markup=back_to_nutrition(),
    )


# ================= НОВЫЙ ХЭНДЛЕР ДЛЯ ПРИЁМА ФОТОГРАФИЙ ЕДЫ =================
@router.message(F.photo)
async def process_food_photo_ai(message: Message, bot: Bot, state: FSMContext):
    # Сбрасываем любые текстовые ожидания, если пользователь просто скинул фото
    await state.clear()
    
    thinking_msg = await message.answer("📸 *Изучаю фотографию вашего блюда через ИИ...*")
    
    try:
        # Скачиваем фотографию самого высокого качества из сообщения Telegram в буфер памяти
        photo = message.photo[-1]
        file_in_memory = io.BytesIO()
        await bot.download(photo, destination=file_in_memory)
        image_bytes = file_in_memory.getvalue()
        
        # Передаем байты изображения в нашу функцию для фото в Gemini 3.6 Flash
        estimation = await estimate_meal_from_photo(image_bytes)
        
        # Сохраняем рассчитанные по фотографии КБЖУ в вашу асинхронную базу данных SQLAlchemy
        async with async_session() as session:
            result = await session.execute(
                select(User).where(User.telegram_id == message.from_user.id)
            )
            user = result.scalar_one()

            meal = Meal(
                user_id=user.id,
                text_description=f"Фото: {estimation['title']}",
                calories=estimation["calories"],
                protein=estimation["protein"],
                fat=estimation["fat"],
                carbs=estimation["carbs"],
            )
            session.add(meal)
            await session.commit()
            
        await thinking_msg.edit_text(
            f"📸 **Еда успешно распознана по фотографии!**\n\n"
            f"🍳 **{estimation['title']}**\n"
            f"🔥 Калории: {estimation['calories']:.0f} ккал\n"
            f"🥩 Белки: {estimation['protein']:.1f} г\n"
            f"🧈 Жиры: {estimation['fat']:.1f} г\n"
            f"🍞 Углеводы: {estimation['carbs']:.1f} г\n\n"
            f"Записал в базу данных и обновил твою статистику! ✅",
            reply_markup=back_to_nutrition(),
        )
    except Exception as e:
        print(f"[PHOTO HANDLER ERROR]: {e}")
        await thinking_msg.edit_text(
            "❌ Не удалось распознать еду на фото. Попробуйте сделать снимок ближе, "
            "четче или пришлите описание блюда текстом.",
            reply_markup=back_to_nutrition()
        )


# --- История записей ---

@router.callback_query(F.data == "nutrition_history")
async def show_history(callback: CallbackQuery) -> None:
    user = await get_user(callback.from_user.id)

    async with async_session() as session:
        result = await session.execute(
            select(Meal)
            .where(Meal.user_id == user.id)
            .order_by(Meal.created_at.desc())
            .limit(10)
        )
        meals = result.scalars().all()

    if not meals:
        await callback.message.edit_text(
            "Пока нет ни одной записи о еде.", reply_markup=back_to_nutrition()
        )
        await callback.answer()
        return

    lines = ["📜 Последние записи:\n"]
    for meal in meals:
        date_str = meal.created_at.strftime("%d.%m %H:%M")
        lines.append(
            f"{date_str} — «{meal.text_description}»\n"
            f"   {meal.calories:.0f} ккал | Б {meal.protein:.0f} / "
            f"Ж {meal.fat:.0f} / У {meal.carbs:.0f}"
        )

    await callback.message.edit_text("\n".join(lines), reply_markup=back_to_nutrition())
    await callback.answer()


# --- Статистика по периодам ---

@router.callback_query(F.data == "nutrition_stats")
async def choose_stats_period(callback: CallbackQuery) -> None:
    await callback.message.edit_text(
        "За какой период показать статистику?", reply_markup=stats_period_menu()
    )
    await callback.answer()


PERIOD_DAYS = {
    "stats_day": 1,
    "stats_week": 7,
    "stats_month": 30,
    "stats_year": 365,
}

PERIOD_LABELS = {
    "stats_day": "за день",
    "stats_week": "за неделю",
    "stats_month": "за месяц",
    "stats_year": "за год",
}


@router.callback_query(F.data.in_(PERIOD_DAYS.keys()))
async def show_stats(callback: CallbackQuery) -> None:
    days = PERIOD_DAYS[callback.data]
    label = PERIOD_LABELS[callback.data]
    since = datetime.utcnow() - timedelta(days=days)

    user = await get_user(callback.from_user.id)

    async with async_session() as session:
        result = await session.execute(
            select(
                func.count(Meal.id),
                func.sum(Meal.calories),
                func.sum(Meal.protein),
                func.sum(Meal.fat),
                func.sum(Meal.carbs),
                func.count(func.distinct(func.date(Meal.created_at))),
            ).where(Meal.user_id == user.id, Meal.created_at >= since)
        )
        count, total_cal, total_protein, total_fat, total_carbs, days_with_records = result.one()

    if not count:
        await callback.message.edit_text(
            f"Нет записей {label}.", reply_markup=stats_period_menu()
        )
        await callback.answer()
        return

    total_cal = total_cal or 0
    total_protein = total_protein or 0
    total_fat = total_fat or 0
    total_carbs = total_carbs or 0
    days_with_records = days_with_records or 1

    avg_cal_per_day = total_cal / days_with_records

    text = (
        f"📊 Статистика {label}\n\n"
        f"Записей: {count}\n"
        f"🔥 Всего калорий: {total_cal:.0f} ккал\n"
        f"📆 В среднем в день: {avg_cal_per_day:.0f} ккал\n\n"
        f"БЖУ за период:\n"
        f"🥩 Белки: {total_protein:.0f} г\n"
        f"🧈 Жиры: {total_fat:.0f} г\n"
        f"🍞 Углеводы: {total_carbs:.0f} г"
    )

    if user.daily_calorie_goal:
        diff = avg_cal_per_day - user.daily_calorie_goal
        sign = "+" if diff >= 0 else ""
        text += f"\n\n🎯 Цель: {user.daily_calorie_goal} ккал/день ({sign}{diff:.0f} в среднем)"

    await callback.message.edit_text(text, reply_markup=stats_period_menu())
    await callback.answer()
