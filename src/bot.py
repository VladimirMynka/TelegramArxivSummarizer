import asyncio
import logging

import arxiv
from telegram import Bot, Update
from telegram.ext import ContextTypes

from src.ai import summarize_article
from src.arxiv_monitor import (
    fetch_by_github,
    fetch_by_id,
    fetch_by_url,
    fetch_new_articles,
)
from src.config import CHANNEL_ID, CHECK_INTERVAL
from src.database import add_article, get_article
from src.pdf import extract_text_from_pdf


async def process_articles(articles: list, bot: Bot):
    for article in articles:
        logging.info(f"Обрабатывается статья: {article.title}")

        existing = await get_article(article.get_short_id())
        if existing:
            logging.info(f"Статья {article.get_short_id()} уже обработана")
            continue  # Уже обработано

        # Получение ссылок (если возможно)
        references = []  # Требует парсинга PDF или наличия ссылок в arXiv API

        # Основное суммирование
        summary = await summarize_article(
            {
                "id": article.get_short_id(),
                "title": article.title,
                "summary": article.summary,
                "text": extract_text_from_pdf(
                    article.download_pdf(filename="temp.pdf")
                ),
                "authors": [author.name for author in article.authors],
                "published": article.published.isoformat(),
                "references": references,
            },
            references_summaries=None,
        )  # Пока без ссылок

        logging.info(f"Статья {article.get_short_id()} обработана")

        article_data = {
            "id": article.get_short_id(),
            "title": article.title,
            "summary": summary,
            "authors": [author.name for author in article.authors],
            "published": article.published.isoformat(),
            "references": references,
        }

        await add_article(article_data)

        logging.info(f"Статья {article.get_short_id()} добавлена в базу")

        # Публикация в Telegram
        message = (
            f"*{article.title}*\n"
            f"Ссылка: {article.pdf_url}\n"
            f"Авторы: {', '.join(article_data['authors'])}\n"
            f"Опубликовано: {article_data['published']}\n\n"
            f"{article_data['summary']}"
        )
        await bot.send_message(chat_id=CHANNEL_ID, text=message, parse_mode="Markdown")
        logging.info(f"Статья {article.get_short_id()} опубликована в Telegram")


# Асинхронная функция обработки новых статей
async def process_new(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logging.info("Достаю новые статьи")
    bot = context.bot
    articles = fetch_new_articles()
    await process_articles(articles, bot)


# Асинхронная функция обработки статьи по ID
async def process_by_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logging.info("Обрабатываю по айди")
    bot = context.bot
    arxiv_id = context.args[0] if context.args else None
    if arxiv_id:
        article = fetch_by_id(arxiv_id)
        await process_articles([article], bot)
    else:
        await update.message.reply_text("Пожалуйста, укажите ID статьи.")


# Асинхронная функция обработки статьи по URL
async def process_by_url(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logging.info("Обрабатываю по url")
    bot = context.bot
    url = context.args[0] if context.args else None
    if url:
        article = fetch_by_url(url)
        await process_articles([article], bot)
    else:
        await update.message.reply_text("Пожалуйста, укажите URL статьи.")


# Асинхронная функция обработки статей по GitHub URL
async def process_by_github(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logging.info("Обрабатываю по гитхабу")
    bot = context.bot
    url = context.args[0] if context.args else None
    if url:
        articles = fetch_by_github(url)
        await process_articles(articles, bot)
    else:
        await update.message.reply_text("Пожалуйста, укажите GitHub URL.")


# Асинхронная функция мониторинга
async def monitor(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    while True:
        try:
            await process_new(update, context)
        except Exception as e:
            logging.error(f"Ошибка при обработке статей: {e}")
        await asyncio.sleep(CHECK_INTERVAL)
