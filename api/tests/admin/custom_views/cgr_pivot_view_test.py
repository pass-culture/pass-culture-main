from unittest.mock import patch

from freezegun import freeze_time

import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.providers.factories as providers_factories
import pcapi.core.providers.models as providers_models
import pcapi.core.providers.repository as providers_repository
from pcapi.core.users.factories import AdminFactory

from tests.conftest import TestClient
from tests.conftest import clean_database
from tests.connectors.cgr import soap_definitions
from tests.local_providers.cinema_providers.cgr import fixtures


class CreateCGRPivotTest:
    @clean_database
    @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
    @patch("flask.flash")
    def test_create_cgr_information_api_ok(self, flash_mock, _mocked_validate_csrf_token, requests_mock, app):
        AdminFactory(email="admin@example.fr")
        venue = offerers_factories.VenueFactory()
        requests_mock.get("https://example.com/web_service?wsdl", text=soap_definitions.WEB_SERVICE_DEFINITION)
        requests_mock.post(
            "https://example.com/web_service", text=fixtures.cgr_response_template([fixtures.FILM_138473])
        )

        data = {
            "venue_id": venue.id,
            "cinema_id": "12",
            "cinema_url": "https://example.com/web_service/",  # with trailing slash
            "cinema_password": "strongPassword",
        }
        client = TestClient(app.test_client()).with_session_auth("admin@example.fr")
        response = client.post("/pc/back-office/cgr/new", form=data)

        assert response.status_code == 302
        cinema_provider_pivot = providers_models.CinemaProviderPivot.query.filter(
            providers_models.CinemaProviderPivot.venueId == venue.id
        ).one()
        assert cinema_provider_pivot.idAtProvider == "12"
        cgr_cinema_details = providers_models.CGRCinemaDetails.query.filter(
            providers_models.CGRCinemaDetails.cinemaProviderPivotId == cinema_provider_pivot.id
        ).one()
        assert cgr_cinema_details.cinemaUrl == "https://example.com/web_service"
        assert cgr_cinema_details.numCinema == 999
        assert cgr_cinema_details.password == "strongPassword"
        flash_mock.assert_called_once_with("Connexion à l'API CGR OK.")

    @clean_database
    @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
    @patch("flask.flash")
    def test_create_cgr_information_api_ko(self, flash_mock, _mocked_validate_csrf_token, requests_mock, app):
        AdminFactory(email="admin@example.fr")
        venue = offerers_factories.VenueFactory()

        data = {
            "venue_id": venue.id,
            "cinema_id": "12",
            "cinema_url": "https://example.com/wrong/ws",
            "cinema_password": "strongPassword",
        }
        client = TestClient(app.test_client()).with_session_auth("admin@example.fr")
        response = client.post("/pc/back-office/cgr/new", form=data)

        assert response.status_code == 302
        cinema_provider_pivot = providers_models.CinemaProviderPivot.query.filter(
            providers_models.CinemaProviderPivot.venueId == venue.id
        ).one()
        assert cinema_provider_pivot.idAtProvider == "12"
        cgr_cinema_details = providers_models.CGRCinemaDetails.query.filter(
            providers_models.CGRCinemaDetails.cinemaProviderPivotId == cinema_provider_pivot.id
        ).one()
        assert cgr_cinema_details.cinemaUrl == "https://example.com/wrong/ws"
        assert cgr_cinema_details.password == "strongPassword"
        flash_mock.assert_called_once_with("Connexion à l'API CGR KO.", "error")

    @clean_database
    @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
    def test_id_at_provider_unicity(self, _mocked_validate_csrf_token, app):
        AdminFactory(email="user@example.com")
        venue = offerers_factories.VenueFactory()
        cgr_provider = providers_repository.get_provider_by_local_class("CGRStocks")
        _cinema_provider_pivot = providers_factories.CinemaProviderPivotFactory(
            venue=venue, provider=cgr_provider, idAtProvider="cinema_test"
        )
        venue_2 = offerers_factories.VenueFactory()

        data = {
            "venue_id": venue_2.id,
            "account_id": "account_test",
            "cinema_id": "cinema_test",
            "cinema_password": "password_test",
        }
        client = TestClient(app.test_client()).with_session_auth("user@example.com")
        response = client.post("/pc/back-office/cgr/new", form=data)

        assert response.status_code == 200
        assert "Cet identifiant cinéma existe déjà pour un autre lieu" in response.data.decode("utf8")
        assert providers_models.CinemaProviderPivot.query.count() == 1

    @clean_database
    @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
    def test_create_cgr_information_when_venue_already_has_cinema_provider(self, _mocked_validate_csrf_token, app):
        AdminFactory(email="user@example.com")
        venue = offerers_factories.VenueFactory()
        cgr_provider = providers_repository.get_provider_by_local_class("CGRStocks")
        _cinema_provider_pivot = providers_factories.CinemaProviderPivotFactory(
            venue=venue, provider=cgr_provider, idAtProvider="cinema1_test"
        )

        data = {
            "venue_id": venue.id,
            "cinema_id": "cinema2_test",
            "cinema_url": "https://example.com",
            "cinema_password": "strongPassword",
        }

        client = TestClient(app.test_client()).with_session_auth("user@example.com")
        response = client.post("/pc/back-office/cgr/new", form=data)
        assert response.status_code == 200
        assert "Des identifiants cinéma existent déjà pour ce lieu id=" in response.data.decode("utf8")
        assert providers_models.CinemaProviderPivot.query.count() == 1


class EditCGRPivotTest:
    @clean_database
    @freeze_time("2022-10-12 17:09:25")
    @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
    @patch("flask.flash")
    def test_update_cgr_information(self, flash_mock, _mocked_validate_csrf_token, requests_mock, app):
        AdminFactory(email="admin@example.fr")
        cgr_provider = providers_repository.get_provider_by_local_class("CGRStocks")
        venue = offerers_factories.VenueFactory()
        cinema_provider_pivot = providers_factories.CinemaProviderPivotFactory(
            venue=venue, provider=cgr_provider, idAtProvider="12"
        )
        cgr_cinema_details = providers_factories.CGRCinemaDetailsFactory(
            cinemaProviderPivot=cinema_provider_pivot, cinemaUrl="https://example.com", password="weakPassword"
        )
        requests_mock.get("https://new-url.com/web_service?wsdl", text=soap_definitions.WEB_SERVICE_DEFINITION)
        requests_mock.post(
            "https://new-url.com/web_service", text=fixtures.cgr_response_template([fixtures.FILM_138473])
        )

        data = {
            "venue_id": venue.id,
            "cinema_id": "13",
            "cinema_url": "https://new-url.com/web_service",
            "cinema_password": "strongPassword",
        }

        client = TestClient(app.test_client()).with_session_auth("admin@example.fr")
        response = client.post(f"/pc/back-office/cgr/edit/?id={cgr_cinema_details.id}", form=data)

        assert response.status_code == 302
        assert cinema_provider_pivot.idAtProvider == "13"
        assert cgr_cinema_details.cinemaUrl == "https://new-url.com/web_service"
        assert cgr_cinema_details.numCinema == 999
        assert cgr_cinema_details.password == "strongPassword"
        flash_mock.assert_called_once_with("Connexion à l'API CGR OK.")

    @clean_database
    @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
    def test_cannot_reuse_cinema_id_at_provider(self, _mocked_validate_csrf_token, app):
        AdminFactory(email="user@example.com")
        cgr_provider = providers_repository.get_provider_by_local_class("CGRStocks")

        venue_1 = offerers_factories.VenueFactory()
        cinema_id_1 = "cinema_1"
        cinema_provider_pivot_1 = providers_factories.CGRCinemaProviderPivotFactory(
            venue=venue_1, provider=cgr_provider, idAtProvider=cinema_id_1
        )
        _cgr_cinema_details_1 = providers_factories.CGRCinemaDetailsFactory(
            cinemaProviderPivot=cinema_provider_pivot_1,
            cinemaUrl="https://example.com/",
        )
        venue_2 = offerers_factories.VenueFactory()
        cinema_id_2 = "cinema_2"
        cinema_provider_pivot_2 = providers_factories.CinemaProviderPivotFactory(
            venue=venue_2, provider=cgr_provider, idAtProvider=cinema_id_2
        )
        cgr_cinema_details_2 = providers_factories.CGRCinemaDetailsFactory(
            cinemaProviderPivot=cinema_provider_pivot_2,
            cinemaUrl="https://another-example.com/",
        )

        data = {
            "venue_id": venue_2.id,
            "cinema_id": cinema_id_1,
            "cinema_url": "https://another-example.com/",
        }

        client = TestClient(app.test_client()).with_session_auth("user@example.com")
        response = client.post(f"/pc/back-office/cgr/edit/?id={cgr_cinema_details_2.id}", form=data)

        # no changes
        assert cinema_provider_pivot_2.idAtProvider == cinema_id_2
        assert cgr_cinema_details_2.cinemaUrl == "https://another-example.com/"
        assert response.status_code == 200  # no redirect
        assert "Cet identifiant cinéma existe déjà pour un autre lieu" in response.data.decode("utf8")


class DeleteCGRPivotTest:
    @clean_database
    @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
    def test_delete_cgr_information(self, _mocked_validate_csrf_token, app):
        AdminFactory(email="admin@example.fr")
        cgr_provider = providers_repository.get_provider_by_local_class("CGRStocks")
        venue = offerers_factories.VenueFactory()
        cinema_provider_pivot = providers_factories.CinemaProviderPivotFactory(
            venue=venue, provider=cgr_provider, idAtProvider="12"
        )
        cgr_cinema_details = providers_factories.CGRCinemaDetailsFactory(
            cinemaProviderPivot=cinema_provider_pivot,
            cinemaUrl="https://example.com/",
        )

        client = TestClient(app.test_client()).with_session_auth("admin@example.fr")
        response = client.post("/pc/back-office/cgr/delete", form={"id": cgr_cinema_details.id})

        assert response.status_code == 302
        assert providers_models.CGRCinemaDetails.query.count() == 0
        assert providers_models.CinemaProviderPivot.query.count() == 0

    @clean_database
    @patch("wtforms.csrf.session.SessionCSRF.validate_csrf_token")
    def test_should_not_delete_cgr_pivot_when_venue_provider_exist(self, _mocked_validate_csrf_token, app):
        AdminFactory(email="admin@example.fr")
        cgr_provider = providers_repository.get_provider_by_local_class("CGRStocks")
        venue = offerers_factories.VenueFactory()
        cinema_provider_pivot = providers_factories.CinemaProviderPivotFactory(
            venue=venue, provider=cgr_provider, idAtProvider="12"
        )
        cgr_cinema_details = providers_factories.CGRCinemaDetailsFactory(
            cinemaProviderPivot=cinema_provider_pivot,
            cinemaUrl="https://example.com/",
        )
        providers_factories.VenueProviderFactory(venue=venue, provider=cgr_provider)

        client = TestClient(app.test_client()).with_session_auth("admin@example.fr")
        response = client.post("/pc/back-office/cgr/delete", form={"id": cgr_cinema_details.id})

        assert response.status_code == 302
        assert providers_models.CGRCinemaDetails.query.count() == 1
        assert providers_models.CinemaProviderPivot.query.count() == 1
