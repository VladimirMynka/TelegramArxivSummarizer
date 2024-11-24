import asyncio

from telegram.ext import ApplicationBuilder, CommandHandler

from src.bot import (
    monitor,
    process_by_github,
    process_by_id,
    process_by_url,
    process_new,
)
from src.config import TELEGRAM_BOT_TOKEN
from src.database import init_db

if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("new", process_new))
    app.add_handler(CommandHandler("id", process_by_id))
    app.add_handler(CommandHandler("url", process_by_url))
    app.add_handler(CommandHandler("github", process_by_github))
    app.add_handler(CommandHandler("monitor", monitor))

    app.run_polling()
