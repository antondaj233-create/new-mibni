import sys
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Добавляем путь к legacy, чтобы FastAPI мог импортировать модули базы данных
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'legacy'))

from database.db import async_session
from database.models import User, Meal
from sqlalchemy import select, func
from datetime import datetime

app = FastAPI(docs_url="/api/docs", openapi_url="/api/openapi.json")

# Настройка CORS, чтобы фронтенд Next.js мог делать запросы к бэкенду
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_headers=["*"],
)

# Модель для валидации входящих данных КБЖУ от фронтенда
class MealCreate(BaseModel):
    telegram_id: int
    title: str
    calories: int
    protein: int
    fat: int
    carbs: int

@app.get("/api/user/{telegram_id}")
async def get_user_stats(telegram_id: int):
    """Получение КБЖУ за сегодняшний день для конкретного пользователя"""
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    
    async with async_session() as session:
        # Ищем пользователя
        user_res = await session.execute(select(User).where(User.telegram_id == telegram_id))
        user = user_res.scalar_one_or_none()
        
        if not user:
            return {
                "target_calories": 2610,
                "current_calories": 0,
                "protein": 0, "fat": 0, "carbs": 0,
                "username": "Атлет"
            }
            
        # Считаем сумму КБЖУ за сегодня
        meals_res = await session.execute(
            select(
                func.sum(Meal.calories),
                func.sum(Meal.protein),
                func.sum(Meal.fat),
                func.sum(Meal.carbs)
            ).where(Meal.user_id == user.id, Meal.created_at >= today_start)
        )
        cur_cal, cur_p, cur_f, cur_c = meals_res.one()
        
    return {
        "username": user.username or "Атлет",
        "target_calories": int(user.daily_calorie_goal or 2610),
        "current_calories": int(cur_cal or 0),
        "protein": int(cur_p or 0),
        "fat": int(cur_f or 0),
        "carbs": int(cur_c or 0)
    }
