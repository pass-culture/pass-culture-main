import pytest

from pcapi.core import testing
import pcapi.core.offerers.factories as offerers_factories


@pytest.mark.usefixtures("db_session")
class CollectiveOffersGetCategoriesTest:
    def test_list_categories(self, client):
        offerer = offerers_factories.OffererFactory()
        offerers_factories.ApiKeyFactory(offerer=offerer)

        num_queries = 1  # select api_key, offerer and provider
        num_queries += 1  # select features
        with testing.assert_num_queries(num_queries):
            response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get(
                "/v2/collective/categories"
            )
            assert response.status_code == 200

        assert response.json == [
            {"id": "BEAUX_ARTS", "name": "Beaux-arts"},
            {"id": "CARTE_JEUNES", "name": "Carte jeunes"},
            {"id": "CINEMA", "name": "Cinéma"},
            {"id": "CONFERENCE", "name": "Conférences, rencontres"},
            {"id": "FILM", "name": "Films, vidéos"},
            {"id": "INSTRUMENT", "name": "Instrument de musique"},
            {"id": "JEU", "name": "Jeux"},
            {"id": "LIVRE", "name": "Livre"},
            {"id": "MEDIA", "name": "Médias"},
            {"id": "MUSEE", "name": "Musée, patrimoine, architecture, arts visuels"},
            {"id": "MUSIQUE_ENREGISTREE", "name": "Musique enregistrée"},
            {"id": "MUSIQUE_LIVE", "name": "Musique live"},
            {"id": "PRATIQUE_ART", "name": "Pratique artistique"},
            {"id": "SPECTACLE", "name": "Spectacle vivant"},
        ]

    def test_list_categories_user_auth_returns_401(self, client):
        user_offerer = offerers_factories.UserOffererFactory()
        offerers_factories.ApiKeyFactory(offerer=user_offerer.offerer)

        client = client.with_session_auth(user_offerer.user.email)
        with testing.assert_num_queries(testing.AUTHENTICATION_QUERIES):
            response = client.get("/v2/collective/categories")
            assert response.status_code == 401

    def test_list_categories_anonymous_returns_401(self, client):
        with testing.assert_num_queries(0):
            response = client.get("/v2/collective/categories")
            assert response.status_code == 401
