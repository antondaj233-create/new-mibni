import asyncio
import json
import re

from google import genai
from google.genai import types

# Твой рабочий API-ключ от Google AI Studio
GEMINI_API_KEY = "AQ.Ab8RN6I6pm1auCzSzpkfabRwH8iEt4QK-w-O7Vv-wslO8B_FgA"
ai_client = genai.Client(api_key=GEMINI_API_KEY)


class NutritionEstimationError(Exception):
    """Кастомное исключение для ошибок распознавания еды"""

    pass


# Универсальный чистильщик JSON от ИИ
def parse_ai_json(raw_text: str) -> dict:
    match = re.search(r"\{.*\}", raw_text.strip(), re.DOTALL)
    if not match:
        raise NutritionEstimationError("ИИ вернул ответ без JSON-структуры")

    data = json.loads(match.group(0))
    p = int(data.get("proteins", 0) or data.get("protein", 0))
    f = int(data.get("fats", 0) or data.get("fat", 0))
    c = int(data.get("carbs", 0) or data.get("carb", 0))

    return {
        "calories": int(data.get("calories", 0)),
        "protein": p,
        "proteins": p,
        "fat": f,
        "fats": f,
        "carb": c,
        "carbs": c,
        "title": str(data.get("title", "Блюдо")),
    }


# Функция для ТЕКСТА
async def estimate_meal(food_text: str) -> dict:
    prompt = (
        f"Посчитай примерное КБЖУ для блюда: '{food_text}'. "
        "Ты должен вернуть ответ СТРОГО в формате JSON, без какого-либо другого текста, без приветствий и без разметки markdown. "
        "Формат ответа: {\"calories\": число, \"proteins\": число, \"fats\": число, \"carbs\": число, \"title\": \"название\"}"
    )
    try:
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: ai_client.models.generate_content(
                model="gemini-3.6-flash", contents=prompt
            ),
        )
        return parse_ai_json(response.text)
    except Exception as e:
        raise NutritionEstimationError(f"Ошибка распознавания текста: {e}")


# ПОЛНОСТЬЮ ИСПРАВЛЕННАЯ ФУНКЦИЯ ДЛЯ ФОТО (без PIL)
async def estimate_meal_from_photo(image_bytes: bytes) -> dict:
    """Функция распознавания КБЖУ еды по фотографии через ИИ Gemini"""
    prompt = (
        "Посмотри на эту фотографию еды. Определи, что это за блюдо, и посчитай его примерный вес и КБЖУ. "
        "Ты должен вернуть ответ СТРОГО в формате JSON, без какого-либо другого текста, без приветствий и без разметки markdown. "
        "Формат ответа: {\"calories\": число, \"proteins\": число, \"fats\": число, \"carbs\": число, \"title\": \"название блюда\"}"
    )
    try:
        # Упаковываем байты картинки в формат, который понимает SDK Google
        image_part = types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg")

        loop = asyncio.get_event_loop()
        # Отправляем текстовый промпт и бинарную картинку
        response = await loop.run_in_executor(
            None,
            lambda: ai_client.models.generate_content(
                model="gemini-3.6-flash", contents=[prompt, image_part]
            ),
        )
        return parse_ai_json(response.text)
    except Exception as e:
        print(f"[AI PHOTO ERROR] Ошибка: {e}")
        raise NutritionEstimationError(f"Ошибка распознавания фото: {e}")
