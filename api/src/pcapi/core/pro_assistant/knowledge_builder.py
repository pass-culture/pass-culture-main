"""Build the pro assistant knowledge files from public sources.

Only public content is fetched: the cultural partners categories of the
public help center (Zendesk Help Center API, no authentication).
"""

import json
import logging
import re

from bs4 import BeautifulSoup

from pcapi.core.pro_assistant import knowledge
from pcapi.utils import requests


logger = logging.getLogger(__name__)

HELP_CENTER_BASE_URL = "https://aide.passculture.app/api/v2/help_center/fr"
HELP_CENTER_CATEGORY_IDS = (
    "4412007116945",  # Acteurs culturels
    "4410482280977",  # Acteurs culturels - Tout savoir sur le pass Culture collectif
)
REQUEST_TIMEOUT_IN_SECONDS = 30


def _get_all_pages(url: str, key: str) -> list[dict]:
    items: list[dict] = []
    next_url: str | None = url
    while next_url:
        response = requests.get(next_url, timeout=REQUEST_TIMEOUT_IN_SECONDS)
        response.raise_for_status()
        data = response.json()
        items.extend(data[key])
        next_url = data.get("next_page")
    return items


def html_to_text(html: str) -> str:
    soup = BeautifulSoup(html or "", "html.parser")
    for tag in soup(["img", "script", "style", "iframe", "video", "svg"]):
        tag.decompose()
    for level in range(1, 7):
        for tag in soup.find_all(f"h{level}"):
            tag.insert_before("\n\n" + "#" * min(level + 1, 6) + " ")
            tag.insert_after("\n\n")
    for tag in soup.find_all("li"):
        tag.insert_before("\n- ")
    for tag in soup.find_all(["p", "table", "ul", "ol", "blockquote"]):
        tag.insert_after("\n\n")
    for tag in soup.find_all(["div", "tr"]):
        tag.insert_after("\n")
    for tag in soup.find_all("br"):
        tag.replace_with("\n")
    text = soup.get_text()
    text = re.sub(r"[ \t\u00a0\u200b]+", " ", text)
    text = re.sub(r" *\n *", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def fetch_help_center_articles() -> list[dict]:
    articles = []
    for category_id in HELP_CENTER_CATEGORY_IDS:
        sections = _get_all_pages(
            f"{HELP_CENTER_BASE_URL}/categories/{category_id}/sections.json?per_page=100", "sections"
        )
        section_names = {section["id"]: section["name"] for section in sections}
        raw_articles = _get_all_pages(
            f"{HELP_CENTER_BASE_URL}/categories/{category_id}/articles.json?per_page=100", "articles"
        )
        for raw_article in raw_articles:
            if raw_article.get("draft"):
                continue
            articles.append(
                {
                    "id": str(raw_article["id"]),
                    "title": raw_article["title"].strip(),
                    "section": section_names.get(raw_article["section_id"], ""),
                    "url": raw_article["html_url"],
                    "updated_at": raw_article["updated_at"][:10],
                    "body": html_to_text(raw_article["body"]),
                }
            )
    # Sorted output keeps the prompt byte-stable between two builds of the same content
    return sorted(articles, key=lambda article: article["id"])


def write_help_center_file(articles: list[dict]) -> None:
    knowledge.KNOWLEDGE_DIR.mkdir(exist_ok=True)
    knowledge.HELP_CENTER_FILE.write_text(
        json.dumps(articles, ensure_ascii=False, indent=1) + "\n",
        encoding="utf-8",
    )
    knowledge.clear_cache()
