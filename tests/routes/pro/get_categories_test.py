import pytest

import pcapi.core.offers.factories as offers_factories

from tests.conftest import TestClient


class Returns200:
    @pytest.mark.usefixtures("db_session")
    def should_return_categories_and_sub_categories(self, app):
        # Given
        venue = offers_factories.VirtualVenueFactory()
        offerer = venue.managingOfferer
        user_offerer = offers_factories.UserOffererFactory(offerer=offerer)
        offers_factories.OfferSubcategoryFactory(
            category__id=1,
            category__name="Musique",
            category__proLabel="Musique",
            category__appLabel="Musique",
            id=1,
            name="Festival",
            proLabel="Festival",
            appLabel="Festival",
        )
        offers_factories.OfferSubcategoryFactory(
            category__id=2,
            category__name="Livre",
            category__proLabel="Livre",
            category__appLabel="Livre",
            id=2,
            name="Livre audio",
            proLabel="Livre audio",
            appLabel="Livre audio",
        )

        # when
        client = TestClient(app.test_client()).with_auth(email=user_offerer.user.email)
        response = client.get("/offers/categories")

        # then
        assert response.status_code == 200
        assert response.json == {
            "categories": [
                {
                    "id": 1,
                    "name": "Musique",
                    "proLabel": "Musique",
                    "appLabel": "Musique",
                },
                {
                    "id": 2,
                    "name": "Livre",
                    "proLabel": "Livre",
                    "appLabel": "Livre",
                },
            ],
            "sub_categories": [
                {
                    "id": 1,
                    "name": "Festival",
                    "isEvent": False,
                    "categoryId": 1,
                    "proLabel": "Festival",
                    "appLabel": "Festival",
                    "conditionalFields": None,
                    "canExpire": True,
                    "isDigital": False,
                    "isDigitalDeposit": False,
                    "isPhysicalDeposit": True,
                    "canBeDuo": False,
                },
                {
                    "id": 2,
                    "name": "Livre audio",
                    "isEvent": False,
                    "categoryId": 2,
                    "proLabel": "Livre audio",
                    "appLabel": "Livre audio",
                    "conditionalFields": None,
                    "canExpire": True,
                    "isDigital": False,
                    "isDigitalDeposit": False,
                    "isPhysicalDeposit": True,
                    "canBeDuo": False,
                },
            ],
        }
