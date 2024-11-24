import logging
import re
from datetime import datetime, timedelta, timezone

import arxiv
import PyPDF2
import requests
from github import Github

from src.config import SEARCH_QUERY

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
    encoding="utf-8",
)


def fetch_new_articles():
    logging.info(f"Поиск новых статей по запросу: {SEARCH_QUERY}")

    client = arxiv.Client(page_size=1000, delay_seconds=10, num_retries=5)
    search = client.results(
        arxiv.Search(
            query=SEARCH_QUERY,
            max_results=1000,
            sort_by=arxiv.SortCriterion.Relevance,
            sort_order=arxiv.SortOrder.Descending,
        )
    )

    results = []
    for i, result in enumerate(search):
        try:
            if result.published < datetime.now(tz=timezone.utc) - timedelta(days=720):
                continue
            results.append(result)
            logging.info(f"Найдена статья {i + 1}: {result.title}")
        except Exception as e:
            logging.error(f"Ошибка при обработке статьи {i + 1}: {e}")

        if i > 300:
            break

    logging.info(f"Найдено {len(results)} новых статей")
    return results


def fetch_by_id(arxiv_id) -> arxiv.Result | None:
    client = arxiv.Client(page_size=1)
    papers = client.results(arxiv.Search(id_list=[arxiv_id]))
    return next(papers) if papers else None


def fetch_by_ids(arxiv_ids) -> list[arxiv.Result] | None:
    client = arxiv.Client(page_size=200)
    papers = client.results(arxiv.Search(id_list=arxiv_ids))
    return list(papers) if papers else None


def extract_arxiv_id_from_url(url) -> str | None:
    # Регулярное выражение для поиска arXiv ID в различных типах ссылок
    match = re.search(r"arxiv\.org/(?:abs|pdf|ftp)/(\d+\.\d+|[a-z\-]+/\d+)", url)
    return match.group(1) if match else None


def fetch_by_url(url) -> arxiv.Result | None:
    arxiv_id = extract_arxiv_id_from_url(url)
    return fetch_by_id(arxiv_id) if arxiv_id else None


def fetch_by_github(github_url, github_token=None) -> list[arxiv.Result] | None:
    g = Github(github_token) if github_token else Github()
    repo_name = github_url.strip("/").split("/")[-2:]
    repo = g.get_repo("/".join(repo_name))

    try:
        readme = repo.get_readme()
    except:
        return []

    readme_content = requests.get(readme.download_url).text
    arxiv_urls = re.findall(
        r"(https?://arxiv\.org/(?:abs|pdf|ftp)/[\w./-]+)", readme_content
    )
    arxiv_ids = [extract_arxiv_id_from_url(url) for url in arxiv_urls]

    # Убираем дубли и неопознанные ссылки
    arxiv_ids = list(filter(None, set(arxiv_ids)))
    
    logging.info(f'Навыделяли {len(arxiv_ids)} ссылок на статьи')

    articles = fetch_by_ids(arxiv_ids)

    return articles
