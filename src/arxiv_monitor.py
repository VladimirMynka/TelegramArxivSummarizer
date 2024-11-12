import asyncio
import logging

import PyPDF2
import arxiv
from telegram import Bot

from src.ai import summarize_article
from src.config import CHANNEL_ID, CHECK_INTERVAL, SEARCH_QUERY
from src.database import add_article, get_article

# Configure logging to output to a file
logging.basicConfig(
    level=logging.INFO,  # Set to DEBUG for more detailed output
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(
            "arxiv_monitor.log"
        ),  # Logs to a file named 'arxiv_monitor.log'
        logging.StreamHandler(),  # Optionally, also log to the console
    ],
)


def extract_text_from_pdf(pdf_path):
    with open(pdf_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            text += page.extract_text()
    return text


def fetch_new_articles():
    logging.info(f"Поиск новых статей по запросу: {SEARCH_QUERY}")

    client = arxiv.Client()
    search = client.results(
        arxiv.Search(
            query=SEARCH_QUERY,
            max_results=20,
            sort_by=arxiv.SortCriterion.Relevance,
            sort_order=arxiv.SortOrder.Descending,
        )
    )

    results = []
    for i, result in enumerate(search):
        logging.info(f"Найдена статья {i + 1}: {result.title}")
        results.append(result)

        if i > 19:
            break

    logging.info(f"Найдено {len(results)} новых статей")
    return results


async def process_articles(bot: Bot):
    articles = fetch_new_articles()
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


async def monitor(bot: Bot):
    while True:
        try:
            await process_articles(bot)
        except Exception as e:
            logging.error(f"Ошибка при обработке статей: {e}")
        await asyncio.sleep(CHECK_INTERVAL)
