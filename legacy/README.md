# Фитнес-бот

## Что уже готово
- Регистрация пользователя при `/start`
- Раздел **Профиль**: единицы измерения, часовой пояс, дневная цель по калориям
- Раздел **Питание**:
  - добавление блюда текстом — калории и БЖУ считает ИИ (Claude)
  - история последних записей
  - статистика за день/неделю/месяц/год + среднее число калорий в день

## Что ещё предстоит (следующий этап)
- Раздел **Тренировки** (дневник тренировок, готовые программы)
- Напоминания по расписанию

## Установка

1. Открой папку `fitness_bot` в VS Code.
2. Создай виртуальное окружение и установи зависимости:
   ```bash
   python -m venv venv
   venv\Scripts\activate      # Windows
   source venv/bin/activate   # macOS/Linux

   pip install -r requirements.txt
   ```
3. Получи токен бота у [@BotFather](https://t.me/BotFather) командой `/newbot`.
4. Получи API-ключ на [console.anthropic.com](https://console.anthropic.com/) (нужна привязанная карта — ИИ-подсчёт калорий делает реальные запросы к API и не бесплатен, но стоит копейки за сообщение).
5. Задай переменные окружения перед запуском (или пропиши значения прямо в `config.py`):
   ```bash
   # Windows (PowerShell)
   $env:BOT_TOKEN="твой_токен"
   $env:ANTHROPIC_API_KEY="твой_ключ"

   # macOS/Linux
   export BOT_TOKEN="твой_токен"
   export ANTHROPIC_API_KEY="твой_ключ"
   ```
6. Запусти бота:
   ```bash
   python bot.py
   ```

Старая версия использовала SQLite; production Mini App переводится на PostgreSQL.

## Структура проекта

```
fitness_bot/
├── bot.py               # точка входа
├── config.py             # токены
├── ai_nutrition.py        # запросы к Claude для подсчёта КБЖУ
├── keyboards.py           # инлайн-клавиатуры
├── database/
│   ├── models.py           # таблицы User, Meal
│   └── db.py               # подключение к SQLite
└── handlers/
    ├── start.py             # /start, главное меню
    ├── profile.py            # раздел профиля
    └── nutrition.py          # питание: добавление, история, статистика
```
