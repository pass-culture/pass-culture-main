import pytest

from pcapi.core.offers.factories import VenueFactory
from pcapi.core.providers.factories import AllocinePivotFactory
from pcapi.core.users.factories import UserFactory
from pcapi.model_creators.provider_creators import activate_provider
from pcapi.utils.human_ids import humanize

from tests.conftest import TestClient


class Get:
    class Returns200:
        @pytest.mark.usefixtures("db_session")
        def when_venue_has_known_allocine_id(self, app):
            # Given
            UserFactory(email="user@test.com")
            venue = VenueFactory(siret="12345678912345")
            AllocinePivotFactory(siret="12345678912345")

            titelive_stocks = activate_provider("TiteLiveStocks")
            allocine_stocks = activate_provider("AllocineStocks")

            # When
            response = (
                TestClient(app.test_client()).with_auth(email="user@test.com").get(f"/providers/{humanize(venue.id)}")
            )

            # Then
            assert response.status_code == 200
            response_json = response.json
            assert response_json == [
                {
                    "enabledForPro": True,
                    "id": humanize(allocine_stocks.id),
                    "isActive": True,
                    "localClass": "AllocineStocks",
                    "name": "Allociné",
                },
                {
                    "enabledForPro": True,
                    "id": humanize(titelive_stocks.id),
                    "isActive": True,
                    "localClass": "TiteLiveStocks",
                    "name": "TiteLive Stocks (Epagine / Place des libraires.com)",
                },
            ]

        @pytest.mark.usefixtures("db_session")
        def when_venue_has_no_allocine_id(self, app):
            # Given
            UserFactory(email="user@test.com")
            venue = VenueFactory()

            titelive_stocks = activate_provider("TiteLiveStocks")
            activate_provider("AllocineStocks")

            # When
            response = (
                TestClient(app.test_client()).with_auth(email="user@test.com").get(f"/providers/{humanize(venue.id)}")
            )

            # Then
            assert response.status_code == 200
            response_json = response.json
            assert response_json == [
                {
                    "enabledForPro": True,
                    "id": humanize(titelive_stocks.id),
                    "isActive": True,
                    "localClass": "TiteLiveStocks",
                    "name": "TiteLive Stocks (Epagine / Place des libraires.com)",
                }
            ]

        class Returns404:
            @pytest.mark.usefixtures("db_session")
            def when_venue_does_not_exists(self, app):
                # Given
                UserFactory(email="user@test.com")
                VenueFactory()
                AllocinePivotFactory()

                activate_provider("TiteLiveStocks")
                activate_provider("AllocineStocks")

                # When
                response = TestClient(app.test_client()).with_auth(email="user@test.com").get("/providers/AZER")

                # Then
                assert response.status_code == 404

        class Returns401:
            @pytest.mark.usefixtures("db_session")
            def when_user_is_not_logged_in(self, app):
                # when
                response = TestClient(app.test_client()).get("/providers/AZER")

                # then
                assert response.status_code == 401
