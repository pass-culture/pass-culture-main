import pytest

from pcapi.core.pro_assistant import knowledge
from pcapi.core.pro_assistant import knowledge_builder
from pcapi.core.pro_assistant import prompt


HELP_CENTER_URL = knowledge_builder.HELP_CENTER_BASE_URL


@pytest.fixture(name="knowledge_dir")
def knowledge_dir_fixture(tmp_path, monkeypatch):
    monkeypatch.setattr(knowledge, "KNOWLEDGE_DIR", tmp_path)
    monkeypatch.setattr(knowledge, "HELP_CENTER_FILE", tmp_path / "help_center.json")
    monkeypatch.setattr(knowledge, "NEWS_FILE", tmp_path / "nouveautes.md")
    knowledge.clear_cache()
    yield tmp_path
    knowledge.clear_cache()


class HtmlToTextTest:
    def test_keeps_structure_and_drops_media(self):
        html = (
            "<h2>Créer une offre</h2><p>Allez dans <strong>Offres</strong>.</p>"
            '<ul><li>Étape 1</li><li>Étape 2</li></ul><img src="x.png"><p>Fin<br>du texte</p>'
        )

        assert knowledge_builder.html_to_text(html) == (
            "### Créer une offre\n\nAllez dans Offres.\n\n- Étape 1\n- Étape 2\n\nFin\ndu texte"
        )


class FetchHelpCenterArticlesTest:
    def test_fetch_and_write_articles(self, requests_mock, knowledge_dir):
        for category_id in knowledge_builder.HELP_CENTER_CATEGORY_IDS:
            requests_mock.get(
                f"{HELP_CENTER_URL}/categories/{category_id}/sections.json?per_page=100",
                json={"sections": [{"id": int(category_id), "name": f"Rubrique {category_id}"}], "next_page": None},
            )
            requests_mock.get(
                f"{HELP_CENTER_URL}/categories/{category_id}/articles.json?per_page=100",
                json={
                    "articles": [
                        {
                            "id": int(category_id) + 1,
                            "title": f" Article {category_id} ",
                            "section_id": int(category_id),
                            "html_url": f"https://aide.passculture.app/hc/fr/articles/{int(category_id) + 1}",
                            "updated_at": "2026-10-01T10:00:00Z",
                            "body": "<p>Contenu</p>",
                            "draft": False,
                        },
                        {"id": 1, "title": "Brouillon", "draft": True},
                    ],
                    "next_page": None,
                },
            )

        articles = knowledge_builder.fetch_help_center_articles()
        knowledge_builder.write_help_center_file(articles)

        help_articles = knowledge.get_help_articles()
        assert len(help_articles) == 2
        article = help_articles["4410482280978"]
        assert article.title == "Article 4410482280977"
        assert article.section == "Rubrique 4410482280977"
        assert article.updated_at == "2026-10-01"
        assert article.body == "Contenu"


class RenderKnowledgeBaseTest:
    def test_render_portal_map_articles_and_news(self, knowledge_dir):
        knowledge_builder.write_help_center_file(
            [
                {
                    "id": "42",
                    "title": "Comment valider une contremarque ?",
                    "section": "Réservations",
                    "url": "https://aide.passculture.app/hc/fr/articles/42",
                    "updated_at": "2026-10-01",
                    "body": "Rendez-vous sur la page Guichet.",
                }
            ]
        )
        knowledge.NEWS_FILE.write_text("## Octobre 2026\nNouvelle page Guichet.", encoding="utf-8")

        rendered = knowledge.render_knowledge_base()

        assert "route_id: desk" in rendered
        assert '<article id="42" titre="Comment valider une contremarque ?"' in rendered
        assert "Rendez-vous sur la page Guichet." in rendered
        assert "Nouvelle page Guichet." in rendered

    def test_system_prompt_is_stable(self, knowledge_dir):
        # The prompt cache only works if the system prompt is byte-identical between requests
        assert prompt.build_system_blocks() == prompt.build_system_blocks()


class CommittedKnowledgeTest:
    def test_contact_support_article_exists(self):
        knowledge.clear_cache()

        assert prompt.CONTACT_SUPPORT_ARTICLE_ID in knowledge.get_help_articles()
