from unittest.mock import patch

import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.providers.factories as providers_factories
import pcapi.core.providers.models as providers_models
from pcapi.core.providers.repository import get_provider_by_local_class
from pcapi.core.users.factories import AdminFactory

from tests.conftest import TestClient
from tests.conftest import clean_database


class CreateCineOfficePivotTest:
    @clean_database
    @patch("flask_wtf.csrf.validate_csrf")
    def test_create_cine_office_information(self, _mocked_validate_csrf_token, app):
        AdminFactory(email="user@example.com")
        venue = offerers_factories.VenueFactory()

        data = {
            "venue_id": venue.id,
            "account_id": "account_test",
            "cinema_id": "cinema_test",
            "api_token": "token_test",
        }
        client = TestClient(app.test_client()).with_session_auth("user@example.com")
        response = client.post("/pc/back-office/cine-office/new", form=data)

        assert response.status_code == 302
        cinema_provider_pivot = providers_models.CinemaProviderPivot.query.filter(
            providers_models.CinemaProviderPivot.venueId == venue.id
        ).one()
        assert cinema_provider_pivot.idAtProvider == "cinema_test"
        cds_cinema_details = providers_models.CDSCinemaDetails.query.filter(
            providers_models.CDSCinemaDetails.cinemaProviderPivotId == cinema_provider_pivot.id
        ).one()
        assert cds_cinema_details.accountId == "account_test"
        assert cds_cinema_details.cinemaApiToken == "token_test"


class EditCineOfficePivotTest:
    @clean_database
    @patch("flask_wtf.csrf.validate_csrf")
    def test_update_cine_office_information(self, _mocked_validate_csrf_token, app):
        AdminFactory(email="user@example.com")
        venue = offerers_factories.VenueFactory()
        cds_provider = get_provider_by_local_class("CDSStocks")
        cinema_provider_pivot = providers_factories.CinemaProviderPivotFactory(
            venue=venue, provider=cds_provider, idAtProvider="cinema_test"
        )
        cds_cinema_details = providers_factories.CDSCinemaDetailsFactory(
            cinemaProviderPivot=cinema_provider_pivot, accountId="cinema_test", cinemaApiToken="token_test"
        )

        data = {
            "venue_id": venue.id,
            "account_id": "new_account_id",
            "cinema_id": "new_cinema_id",
            "api_token": "new_token_id",
        }

        client = TestClient(app.test_client()).with_session_auth("user@example.com")
        response = client.post(f"/pc/back-office/cine-office/edit/?id={cds_cinema_details.id}", form=data)

        assert response.status_code == 302
        assert cinema_provider_pivot.idAtProvider == "new_cinema_id"
        assert cds_cinema_details.accountId == "new_account_id"
        assert cds_cinema_details.cinemaApiToken == "new_token_id"


class DeleteCineOfficePivotTest:
    @clean_database
    @patch("flask_wtf.csrf.validate_csrf")
    def test_delete_cine_office_information(self, _mocked_validate_csrf_token, app):
        AdminFactory(email="admin@example.fr")
        cds_provider = get_provider_by_local_class("CDSStocks")
        venue = offerers_factories.VenueFactory()
        cinema_provider_pivot = providers_factories.CinemaProviderPivotFactory(
            venue=venue, provider=cds_provider, idAtProvider="cinema_test"
        )
        cds_cinema_details = providers_factories.CDSCinemaDetailsFactory(
            cinemaProviderPivot=cinema_provider_pivot, accountId="cinema_test", cinemaApiToken="token_test"
        )

        client = TestClient(app.test_client()).with_session_auth("admin@example.fr")
        response = client.post("/pc/back-office/cine-office/delete", form={"id": cds_cinema_details.id})

        assert response.status_code == 302
        assert providers_models.CDSCinemaDetails.query.count() == 0
        assert providers_models.CinemaProviderPivot.query.count() == 0

    @clean_database
    @patch("flask_wtf.csrf.validate_csrf")
    def test_should_not_delete_cine_office_pivot_when_venue_provider_exist(self, _mocked_validate_csrf_token, app):
        AdminFactory(email="admin@example.fr")
        cds_provider = get_provider_by_local_class("CDSStocks")
        venue = offerers_factories.VenueFactory()
        cinema_provider_pivot = providers_factories.CinemaProviderPivotFactory(
            venue=venue, provider=cds_provider, idAtProvider="cinema_test"
        )
        cds_cinema_details = providers_factories.CDSCinemaDetailsFactory(
            cinemaProviderPivot=cinema_provider_pivot, accountId="cinema_test", cinemaApiToken="token_test"
        )
        providers_factories.VenueProviderFactory(venue=venue, provider=cds_provider)

        client = TestClient(app.test_client()).with_session_auth("admin@example.fr")
        response = client.post("/pc/back-office/cine-office/delete", form={"id": cds_cinema_details.id})

        assert response.status_code == 302
        assert providers_models.CDSCinemaDetails.query.count() == 1
        assert providers_models.CinemaProviderPivot.query.count() == 1
