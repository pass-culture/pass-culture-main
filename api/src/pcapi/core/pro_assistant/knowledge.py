"""Knowledge base given to the pro assistant.

Everything here is public content (help center, public Notion news page, portal
routes). It is rendered once per process into a byte-stable text, so that the
Claude API prompt cache can be reused across requests.
"""

import dataclasses
import functools
import json
import pathlib

from pcapi.core.pro_assistant import portal_map


KNOWLEDGE_DIR = pathlib.Path(__file__).parent / "knowledge"
HELP_CENTER_FILE = KNOWLEDGE_DIR / "help_center.json"
# Manual Markdown export of the Notion "Nouveautés" database (optional)
NEWS_FILE = KNOWLEDGE_DIR / "nouveautes.md"


@dataclasses.dataclass(frozen=True)
class HelpArticle:
    id: str
    title: str
    section: str
    url: str
    updated_at: str
    body: str


@functools.cache
def get_help_articles() -> dict[str, HelpArticle]:
    if not HELP_CENTER_FILE.exists():
        return {}
    raw_articles = json.loads(HELP_CENTER_FILE.read_text(encoding="utf-8"))
    articles = (HelpArticle(**raw_article) for raw_article in raw_articles)
    return {article.id: article for article in sorted(articles, key=lambda article: article.id)}


@functools.cache
def render_knowledge_base() -> str:
    parts = [
        "# Pages du portail pro (route_id utilisables dans `route_ids`)",
        portal_map.render_for_prompt(),
        "# Articles du centre d'aide (id utilisables dans `help_article_ids`)",
    ]
    for article in get_help_articles().values():
        parts.append(
            f'<article id="{article.id}" titre="{article.title}" rubrique="{article.section}" '
            f'mis_a_jour="{article.updated_at}">\n{article.body}\n</article>'
        )
    if NEWS_FILE.exists():
        parts.append("# Nouveautés récentes du portail pro (les plus récentes en premier)")
        parts.append(NEWS_FILE.read_text(encoding="utf-8").strip())
    return "\n\n".join(parts)


def clear_cache() -> None:
    get_help_articles.cache_clear()
    render_knowledge_base.cache_clear()
