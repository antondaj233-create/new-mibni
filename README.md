# Fitness Telegram Mini App — Vercel starter

This project is a first Mini App migration of the supplied aiogram fitness bot.

## What is included
- Next.js Telegram Mini App UI
- Dashboard with calories and macros
- Add meal flow
- History for today's meals
- Day/week/month/year statistics
- Profile display
- Telegram initData signature validation
- Vercel configuration
- Environment variable template

## Important
The original source contained credentials directly in `config.py`. Those credentials must be rotated. Do not put real secrets into Git or the frontend.

## Deploy
1. Upload/import this repository into Vercel.
2. Set `BOT_TOKEN`, `ANTHROPIC_API_KEY` and `DATABASE_URL` in Vercel Environment Variables.
3. Deploy.
4. In @BotFather, set the Mini App URL to the deployed HTTPS URL.
5. The frontend sends Telegram `initData` to the backend and the backend verifies it.

## Production migration still needed
The starter intentionally uses an in-memory store so the UI can be previewed without a database. For real users, replace the storage functions in `api/index.py` with PostgreSQL/Neon and connect the existing `User`/`Meal` schema.

The supplied AI nutrition module can also be moved behind `/api/meals` after choosing the final AI provider/key. Photo recognition should use Telegram's file download on a server-side bot endpoint or a direct image upload endpoint; the secret AI key must never reach the browser.
