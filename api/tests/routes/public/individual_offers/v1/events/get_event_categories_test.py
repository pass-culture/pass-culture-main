import pytest

from pcapi.core import testing
from pcapi.core.categories import subcategories

from tests.routes.public.helpers import PublicAPIEndpointBaseHelper


pytestmark = pytest.mark.usefixtures("db_session")

num_queries = 1  # select api_key, offerer and provider


@pytest.mark.usefixtures("db_session")
class GetEventCategoriesTest(PublicAPIEndpointBaseHelper):
    endpoint_url = "/public/offers/v1/events/categories"
    endpoint_method = "get"

    def test_returns_all_selectable_categories(self):
        plain_api_key, _ = self.setup_provider()

        with testing.assert_num_queries(num_queries):
            response = self.make_request(plain_api_key)
            assert response.status_code == 200

        assert set(subcategory["id"] for subcategory in response.json) == set(
            subcategory_id
            for subcategory_id, subcategory in subcategories.EVENT_SUBCATEGORIES.items()
            if subcategory.is_selectable
        )

    def test_category_serialization(self):
        plain_api_key, _ = self.setup_provider()

        with testing.assert_num_queries(num_queries):
            response = self.make_request(plain_api_key)
            assert response.status_code == 200

        assert response.json == [
            {
                "id": "ATELIER_PRATIQUE_ART",
                "conditionalFields": {"speaker": False},
                "label": "Atelier, stage de pratique artistique",
            },
            {
                "id": "CINE_PLEIN_AIR",
                "conditionalFields": {"author": False, "visa": False, "stageDirector": False},
                "label": "Cinéma plein air",
            },
            {
                "id": "CONCERT",
                "conditionalFields": {
                    "author": False,
                    "musicSubType": False,
                    "musicType": True,
                    "gtl_id": False,
                    "performer": False,
                },
                "label": "Concert",
            },
            {"id": "CONCOURS", "conditionalFields": {}, "label": "Concours - jeux"},
            {"id": "CONFERENCE", "conditionalFields": {"speaker": False}, "label": "Conférence"},
            {
                "id": "EVENEMENT_CINE",
                "conditionalFields": {"author": False, "visa": False, "stageDirector": False},
                "label": "Évènement cinématographique",
            },
            {"id": "EVENEMENT_JEU", "conditionalFields": {}, "label": "Évènements - jeux"},
            {
                "id": "EVENEMENT_MUSIQUE",
                "conditionalFields": {
                    "author": False,
                    "musicSubType": False,
                    "musicType": True,
                    "gtl_id": False,
                    "performer": False,
                },
                "label": "Autre type d'évènement musical",
            },
            {"id": "EVENEMENT_PATRIMOINE", "conditionalFields": {}, "label": "Évènement et atelier patrimoine"},
            {
                "id": "FESTIVAL_ART_VISUEL",
                "conditionalFields": {"author": False, "performer": False},
                "label": "Festival d'arts visuels / arts numériques",
            },
            {
                "id": "FESTIVAL_CINE",
                "conditionalFields": {"author": False, "visa": False, "stageDirector": False},
                "label": "Festival de cinéma",
            },
            {"id": "FESTIVAL_LIVRE", "conditionalFields": {}, "label": "Festival et salon du livre"},
            {
                "id": "FESTIVAL_MUSIQUE",
                "conditionalFields": {
                    "author": False,
                    "musicSubType": False,
                    "musicType": True,
                    "gtl_id": False,
                    "performer": False,
                },
                "label": "Festival de musique",
            },
            {
                "id": "FESTIVAL_SPECTACLE",
                "conditionalFields": {
                    "author": False,
                    "showSubType": True,
                    "showType": True,
                    "stageDirector": False,
                    "performer": False,
                },
                "label": "Festival de spectacle vivant",
            },
            {
                "id": "LIVESTREAM_EVENEMENT",
                "conditionalFields": {
                    "author": False,
                    "showSubType": True,
                    "showType": True,
                    "stageDirector": False,
                    "performer": False,
                },
                "label": "Livestream d'évènement",
            },
            {
                "id": "LIVESTREAM_MUSIQUE",
                "conditionalFields": {
                    "author": False,
                    "musicSubType": False,
                    "musicType": True,
                    "gtl_id": False,
                    "performer": False,
                },
                "label": "Livestream musical",
            },
            {
                "id": "LIVESTREAM_PRATIQUE_ARTISTIQUE",
                "conditionalFields": {},
                "label": "Pratique artistique - livestream",
            },
            {"id": "RENCONTRE_EN_LIGNE", "conditionalFields": {"speaker": False}, "label": "Rencontre en ligne"},
            {"id": "RENCONTRE_JEU", "conditionalFields": {}, "label": "Rencontres - jeux"},
            {"id": "RENCONTRE", "conditionalFields": {"speaker": False}, "label": "Rencontre"},
            {"id": "SALON", "conditionalFields": {"speaker": False}, "label": "Salon, Convention"},
            {
                "id": "SEANCE_CINE",
                "conditionalFields": {"author": False, "visa": False, "stageDirector": False},
                "label": "Séance de cinéma",
            },
            {"id": "SEANCE_ESSAI_PRATIQUE_ART", "conditionalFields": {"speaker": False}, "label": "Séance d'essai"},
            {
                "id": "SPECTACLE_REPRESENTATION",
                "conditionalFields": {
                    "author": False,
                    "showSubType": True,
                    "showType": True,
                    "stageDirector": False,
                    "performer": False,
                },
                "label": "Spectacle, représentation",
            },
            {"id": "VISITE_GUIDEE", "conditionalFields": {}, "label": "Visite guidée"},
            {"id": "VISITE", "conditionalFields": {}, "label": "Visite libre"},
        ]
