from datetime import datetime

from sqlalchemy import BigInteger, Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False, index=True)

    # Настройки профиля
    units = Column(String, default="metric")  # metric (кг) / imperial (фунты)
    timezone = Column(String, default="Europe/Moscow")
    daily_calorie_goal = Column(Integer, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    meals = relationship("Meal", back_populates="user", cascade="all, delete-orphan")


class Meal(Base):
    __tablename__ = "meals"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    text_description = Column(String, nullable=False)
    calories = Column(Float, nullable=False)
    protein = Column(Float, nullable=False)  # г
    fat = Column(Float, nullable=False)  # г
    carbs = Column(Float, nullable=False)  # г

    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    user = relationship("User", back_populates="meals")
