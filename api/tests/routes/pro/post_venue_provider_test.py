from unittest.mock import patch

import pytest

import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.providers.factories as providers_factories
from pcapi.core.providers.factories import CinemaProviderPivotFactory
from pcapi.core.providers.models import Provider
from pcapi.core.providers.models import VenueProvider
from pcapi.core.users import factories as user_factories
from pcapi.models.api_errors import ApiErrors
from pcapi.utils.human_ids import dehumanize
from pcapi.utils.human_ids import humanize

from tests.conftest import TestClient
from tests.conftest import clean_database


class Returns201Test:
    @pytest.mark.usefixtures("db_session")
    @patch("pcapi.workers.venue_provider_job.venue_provider_job.delay")
    @patch("pcapi.core.providers.api._siret_can_be_synchronized")
    def test_when_venue_provider_is_successfully_created(
        self, mock_siret_can_be_synchronized, mock_synchronize_venue_provider, app
    ):
        # Given
        user = user_factories.AdminFactory()
        venue = offerers_factories.VenueFactory(siret="12345678912345")

        provider = providers_factories.APIProviderFactory()

        venue_provider_data = {
            "providerId": humanize(provider.id),
            "venueId": humanize(venue.id),
        }
        mock_siret_can_be_synchronized.return_value = True

        auth_request = TestClient(app.test_client()).with_session_auth(email=user.email)
        # When
        response = auth_request.post("/venueProviders", json=venue_provider_data)

        # Then
        assert response.status_code == 201
        venue_provider = VenueProvider.query.one()
        assert venue_provider.venueId == venue.id
        assert venue_provider.providerId == provider.id
        assert venue_provider.venueIdAtOfferProvider == "12345678912345"
        assert "id" in response.json

        venue_provider_id = response.json["id"]
        mock_synchronize_venue_provider.assert_called_once_with(dehumanize(venue_provider_id))

    @pytest.mark.usefixtures("db_session")
    @patch("pcapi.workers.venue_provider_job.synchronize_venue_provider")
    def test_when_add_allocine_stocks_provider_with_price_but_no_isDuo_config(
        self, mock_synchronize_venue_provider, app
    ):
        # Given
        venue = offerers_factories.VenueFactory(managingOfferer__siren="775671464")
        user = user_factories.AdminFactory()
        providers_factories.AllocineTheaterFactory(siret=venue.siret)
        provider = providers_factories.AllocineProviderFactory()

        venue_provider_data = {"providerId": humanize(provider.id), "venueId": humanize(venue.id), "price": "9.99"}

        auth_request = TestClient(app.test_client()).with_session_auth(email=user.email)

        # When
        response = auth_request.post("/venueProviders", json=venue_provider_data)

        # Then
        assert response.status_code == 201
        json = response.json
        venue_provider = VenueProvider.query.one()
        mock_synchronize_venue_provider.assert_called_once_with(venue_provider)
        assert json["venueId"] == humanize(venue_provider.venueId)

    @pytest.mark.usefixtures("db_session")
    @patch("pcapi.workers.venue_provider_job.synchronize_venue_provider")
    def test_when_add_allocine_stocks_provider_with_default_settings_at_import(
        self, mock_synchronize_venue_provider, app
    ):
        # Given
        venue = offerers_factories.VenueFactory(managingOfferer__siren="775671464")
        user = user_factories.AdminFactory()
        providers_factories.AllocineTheaterFactory(siret=venue.siret)
        provider = providers_factories.AllocineProviderFactory()

        venue_provider_data = {
            "providerId": humanize(provider.id),
            "venueId": humanize(venue.id),
            "price": "9.99",
            "quantity": 50,
            "isDuo": True,
        }

        auth_request = TestClient(app.test_client()).with_session_auth(email=user.email)

        # When
        response = auth_request.post("/venueProviders", json=venue_provider_data)

        # Then
        assert response.status_code == 201
        assert response.json["isDuo"]
        assert response.json["price"] == 9.99
        assert response.json["quantity"] == 50
        venue_provider = VenueProvider.query.one()
        mock_synchronize_venue_provider.assert_called_once_with(venue_provider)

    @pytest.mark.usefixtures("db_session")
    @patch("pcapi.workers.venue_provider_job.venue_provider_job.delay")
    @patch("pcapi.core.providers.api._siret_can_be_synchronized")
    def test_when_no_regression_on_format(self, mock_siret_can_be_synchronized, mock_synchronize_venue_provider, app):
        # Given
        user = user_factories.AdminFactory()
        venue = offerers_factories.VenueFactory(siret="12345678912345")

        provider = providers_factories.APIProviderFactory()

        venue_provider_data = {
            "providerId": humanize(provider.id),
            "venueId": humanize(venue.id),
        }

        auth_request = TestClient(app.test_client()).with_session_auth(email=user.email)
        mock_siret_can_be_synchronized.return_value = True

        # When
        response = auth_request.post("/venueProviders", json=venue_provider_data)

        # Then
        assert response.status_code == 201
        assert set(response.json.keys()) == {
            "dateModifiedAtLastProvider",
            "fieldsUpdated",
            "id",
            "idAtProviders",
            "isActive",
            "isDuo",
            "isFromAllocineProvider",
            "lastProviderId",
            "lastSyncDate",
            "nOffers",
            "price",
            "provider",
            "providerId",
            "quantity",
            "venueId",
            "venueIdAtOfferProvider",
        }
        assert set(response.json["provider"].keys()) == {
            "enabledForPro",
            "id",
            "isActive",
            "localClass",
            "name",
        }

    @pytest.mark.usefixtures("db_session")
    @patch("pcapi.workers.venue_provider_job.venue_provider_job.delay")
    @patch("pcapi.core.providers.api._siret_can_be_synchronized")
    def test_when_venue_id_at_offer_provider_is_ignored_for_pro(
        self, mock_siret_can_be_synchronized, mock_synchronize_venue_provider, app
    ):
        # Given
        user = user_factories.AdminFactory()
        venue = offerers_factories.VenueFactory(siret="12345678912345")

        provider = providers_factories.APIProviderFactory()

        venue_provider_data = {
            "providerId": humanize(provider.id),
            "venueId": humanize(venue.id),
            "venueIdAtOfferProvider": "====VY24G1AGF56",
        }

        auth_request = TestClient(app.test_client()).with_session_auth(email=user.email)
        mock_siret_can_be_synchronized.return_value = True

        # When
        response = auth_request.post("/venueProviders", json=venue_provider_data)

        # Then
        assert response.status_code == 201
        venue_provider = VenueProvider.query.one()
        assert venue_provider.venueId == venue.id
        assert venue_provider.providerId == provider.id
        assert venue_provider.venueIdAtOfferProvider == "12345678912345"
        assert "id" in response.json
        venue_provider_id = response.json["id"]
        mock_synchronize_venue_provider.assert_called_once_with(dehumanize(venue_provider_id))

    @pytest.mark.usefixtures("db_session")
    @patch("pcapi.core.providers.api._siret_can_be_synchronized", lambda *args: True)
    def test_when_add_same_provider(self, client):
        # Given
        admin = user_factories.AdminFactory()
        venue_provider = providers_factories.VenueProviderFactory()

        client = client.with_session_auth(email=admin.email)
        venue_provider_data = {
            "providerId": humanize(venue_provider.providerId),
            "venueId": humanize(venue_provider.venueId),
        }

        # When
        response = client.post("/venueProviders", json=venue_provider_data)

        # Then
        assert response.status_code == 400
        assert response.json == {"global": ["Votre lieu est déjà lié à cette source"]}
        assert venue_provider.venue.venueProviders == [venue_provider]

    @pytest.mark.usefixtures("db_session")
    @patch("pcapi.core.booking_providers.cds.client.get_resource")
    @patch("pcapi.settings.CDS_API_URL", "fakeUrl")
    def test_create_venue_provider_for_cds_cinema(self, mocked_get_resource, client):
        # Given
        user = user_factories.AdminFactory()
        client = client.with_session_auth(email=user.email)
        provider = Provider.query.filter(Provider.localClass == "CDSStocks").first()

        venue = offerers_factories.VenueFactory()
        cds_pivot = CinemaProviderPivotFactory(venue=venue, provider=provider)
        providers_factories.CDSCinemaDetailsFactory(cinemaProviderPivot=cds_pivot, cinemaApiToken="test_token")

        venue_provider_data = {
            "providerId": humanize(provider.id),
            "venueId": humanize(venue.id),
            # TODO AMARINIER : add isDuo to payload when we implement cds modal
        }
        movies_json = [
            {
                "id": 1,
                "title": "Test movie #1",
                "duration": 7200,
                "storyline": "Test description #1",
                "visanumber": "123",
            },
            {
                "id": 2,
                "title": "Test movie #2",
                "duration": 5400,
                "storyline": "Test description #2",
                "visanumber": "456",
            },
        ]

        mocked_get_resource.return_value = movies_json

        # When
        response = client.post("/venueProviders", json=venue_provider_data)

        # Then
        assert response.json["nOffers"] == 2
        assert response.json["providerId"] == humanize(provider.id)
        assert response.json["venueId"] == humanize(venue.id)
        assert response.json["venueIdAtOfferProvider"] == cds_pivot.idAtProvider


class Returns400Test:
    @pytest.mark.usefixtures("db_session")
    def test_when_api_error_raise_when_missing_fields(self, app):
        # Given
        user = user_factories.AdminFactory()
        auth_request = TestClient(app.test_client()).with_session_auth(email=user.email)
        venue_provider_data = {}

        # When
        response = auth_request.post("/venueProviders", json=venue_provider_data)

        # Then
        assert response.status_code == 400
        assert response.json["venueId"] == ["Ce champ est obligatoire"]
        assert response.json["providerId"] == ["Ce champ est obligatoire"]

    @clean_database
    def test_when_add_allocine_stocks_provider_with_wrong_format_price(self, app):
        # Given
        venue = offerers_factories.VenueFactory(managingOfferer__siren="775671464")
        user = user_factories.AdminFactory()
        providers_factories.AllocineTheaterFactory(siret=venue.siret)
        provider = providers_factories.AllocineProviderFactory()

        venue_provider_data = {
            "providerId": humanize(provider.id),
            "venueId": humanize(venue.id),
            "price": "wrong_price",
        }

        auth_request = TestClient(app.test_client()).with_session_auth(email=user.email)

        # When
        response = auth_request.post("/venueProviders", json=venue_provider_data)

        # Then
        assert response.status_code == 400
        assert response.json["global"] == ["Le prix doit être un nombre décimal"]
        assert VenueProvider.query.count() == 0

    @pytest.mark.usefixtures("db_session")
    def test_when_add_allocine_stocks_provider_with_no_price(self, app):
        # Given
        venue = offerers_factories.VenueFactory(managingOfferer__siren="775671464")
        user = user_factories.AdminFactory()
        providers_factories.AllocineTheaterFactory(siret=venue.siret)
        provider = providers_factories.AllocineProviderFactory()

        venue_provider_data = {
            "providerId": humanize(provider.id),
            "venueId": humanize(venue.id),
        }

        auth_request = TestClient(app.test_client()).with_session_auth(email=user.email)

        # When
        response = auth_request.post("/venueProviders", json=venue_provider_data)

        # Then
        assert response.status_code == 400
        assert response.json["price"] == ["Il est obligatoire de saisir un prix."]
        assert VenueProvider.query.count() == 0


class Returns401Test:
    @pytest.mark.usefixtures("db_session")
    def test_when_user_is_not_logged_in(self, app):
        # when
        response = TestClient(app.test_client()).post("/venueProviders")

        # then
        assert response.status_code == 401


class Returns404Test:
    @pytest.mark.usefixtures("db_session")
    def test_when_venue_does_not_exist(self, app):
        # Given
        user = user_factories.AdminFactory()

        provider = providers_factories.APIProviderFactory()

        venue_provider_data = {
            "providerId": humanize(provider.id),
            "venueId": "AZERT",
        }

        auth_request = TestClient(app.test_client()).with_session_auth(email=user.email)

        # When
        response = auth_request.post("/venueProviders", json=venue_provider_data)

        # Then
        assert response.status_code == 404

    @pytest.mark.usefixtures("db_session")
    def test_when_add_allocine_pivot_is_missing(self, app):
        # Given
        venue = offerers_factories.VenueFactory(managingOfferer__siren="775671464")
        user = user_factories.AdminFactory()
        provider = providers_factories.AllocineProviderFactory()

        venue_provider_data = {
            "providerId": humanize(provider.id),
            "venueId": humanize(venue.id),
        }

        auth_request = TestClient(app.test_client()).with_session_auth(email=user.email)

        # When
        response = auth_request.post("/venueProviders", json=venue_provider_data)

        # Then
        assert response.status_code == 404
        assert response.json == {
            "allocine": [
                "Ce lieu n'est pas autorisé à être synchronisé avec Allociné. Veuillez contacter le support si vous souhaitez le faire."
            ]
        }
        assert VenueProvider.query.count() == 0


class Returns422Test:
    @pytest.mark.usefixtures("db_session")
    @patch("pcapi.core.providers.api._siret_can_be_synchronized")
    def test_when_provider_api_not_available(self, mock_siret_can_be_synchronized, app):
        # Given
        user = user_factories.AdminFactory()
        venue = offerers_factories.VenueFactory(siret="12345678912345")

        provider = providers_factories.APIProviderFactory()

        venue_provider_data = {
            "providerId": humanize(provider.id),
            "venueId": humanize(venue.id),
        }

        auth_request = TestClient(app.test_client()).with_session_auth(email=user.email)

        errors = ApiErrors()
        errors.status_code = 422
        errors.add_error(
            "provider",
            "L’importation d’offres avec LesLibraires n’est pas disponible " "pour le SIRET 12345678912345",
        )
        mock_siret_can_be_synchronized.side_effect = [errors]

        # When
        response = auth_request.post("/venueProviders", json=venue_provider_data)

        # Then
        assert response.status_code == 422
        assert response.json["provider"] == [
            "L’importation d’offres avec LesLibraires n’est pas disponible pour le SIRET 12345678912345"
        ]
        assert VenueProvider.query.count() == 0


class ConnectProviderToVenueTest:
    @pytest.mark.usefixtures("db_session")
    @patch("pcapi.core.providers.api._siret_can_be_synchronized")
    @patch("pcapi.core.providers.api.connect_venue_to_provider")
    def test_should_inject_the_appropriate_repository_to_the_usecase(
        self, mocked_connect_venue_to_provider, mock_siret_can_be_synchronized, app
    ):
        # Given
        user = user_factories.AdminFactory()
        venue = offerers_factories.VenueFactory(siret="12345678912345")

        provider = providers_factories.APIProviderFactory()

        venue_provider_data = {
            "providerId": humanize(provider.id),
            "venueId": humanize(venue.id),
        }

        auth_request = TestClient(app.test_client()).with_session_auth(email=user.email)
        mock_siret_can_be_synchronized.return_value = True

        # When
        auth_request.post("/venueProviders", json=venue_provider_data)

        # Then
        mocked_connect_venue_to_provider.assert_called_once_with(venue, provider, None)

    @pytest.mark.usefixtures("db_session")
    def test_should_connect_to_allocine(
        self,
        app,
    ):
        # Given
        user = user_factories.AdminFactory()
        venue = offerers_factories.VenueFactory()
        providers_factories.AllocineTheaterFactory(siret=venue.siret)
        provider = providers_factories.AllocineProviderFactory()

        venue_provider_data = {"providerId": humanize(provider.id), "venueId": humanize(venue.id), "price": "33.33"}

        auth_request = TestClient(app.test_client()).with_session_auth(email=user.email)

        # When
        auth_request.post("/venueProviders", json=venue_provider_data)

        # Then
        assert len(venue.venueProviders) == 1
        assert venue.venueProviders[0].provider == provider
