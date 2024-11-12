import logging
import aiosqlite

DATABASE = "articles.db"


async def init_db():
    logging.info(f"Инициализация базы данных: {DATABASE}")
    async with aiosqlite.connect(DATABASE) as db:
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS articles (
                id TEXT PRIMARY KEY,
                title TEXT,
                summary TEXT,
                authors TEXT,
                published DATE,
                "references" TEXT
            );
        """
        )
        logging.info(f"База данных {DATABASE} инициализирована")
        await db.commit()


async def add_article(article):
    async with aiosqlite.connect(DATABASE) as db:
        await db.execute(
            """
            INSERT OR IGNORE INTO articles (id, title, summary, authors, published, "references")
            VALUES (?, ?, ?, ?, ?, ?)
        """,
            (
                article["id"],
                article["title"],
                article["summary"],
                ", ".join(article["authors"]),
                article["published"],
                ",".join(article.get("references", [])),
            ),
        )
        await db.commit()


async def get_article(article_id):
    logging.info(f"Получение статьи с id: {article_id}")
    try:
        logging.info(f"Подключение к базе данных: {DATABASE}")
        async with aiosqlite.connect(DATABASE) as db:
            logging.info(f"Подключено к базе данных: {DATABASE}")
            async with db.execute(
                "SELECT * FROM articles WHERE id = ?", (article_id,)
            ) as cursor:
                logging.info(f"Выполнено запрос к базе данных: {DATABASE}")
                row = await cursor.fetchone()
                logging.info(f"Результат запроса: {row}")
                if row:
                    return {
                        "id": row[0],
                        "title": row[1],
                        "summary": row[2],
                        "authors": row[3].split(", "),
                        "published": row[4],
                        "references": row[5].split(",") if row[5] else [],
                    }
                return None
    except Exception as e:
        logging.error(f"Ошибка при получении статьи с id {article_id}: {e}")
        return None
