import asyncio

from telegram import Bot

from src.arxiv_monitor import monitor
from src.config import TELEGRAM_BOT_TOKEN
from src.database import init_db


async def main():
    # Инициализация базы данных
    await init_db()

    bot = Bot(token=TELEGRAM_BOT_TOKEN)

    # Запуск мониторинга arXiv
    await monitor(bot)


if __name__ == "__main__":
    asyncio.run(main())
