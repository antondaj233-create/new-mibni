The original fitness_bot.db was found in the uploaded archive. It is not copied into the deployable project because Vercel serverless functions should not use a local SQLite file as persistent production storage.

The old SQLAlchemy schema is preserved in legacy/database/models.py:
- users
- meals

Next step: import the old SQLite rows into PostgreSQL/Neon with the same logical columns.
