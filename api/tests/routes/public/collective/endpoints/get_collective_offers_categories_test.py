import pytest

from pcapi.core import testing
import pcapi.core.offerers.factories as offerers_factories

from tests.routes.public.helpers import PublicAPIEndpointBaseHelper


@pytest.mark.usefixtures("db_session")
class CollectiveOffersGetCategoriesTest(PublicAPIEndpointBaseHelper):
    endpoint_url = "/v2/collective/categories"
    endpoint_method = "get"

    def test_list_categories(self, client):
        plain_api_key, _ = self.setup_provider()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.ApiKeyFactory(offerer=offerer)

        num_queries = 1  # select api_key, offerer and provider
        num_queries += 1  # select features
        with testing.assert_num_queries(num_queries):
            response = client.with_explicit_token(plain_api_key).get(self.endpoint_url)
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
            response = client.get(self.endpoint_url)
            assert response.status_code == 401
