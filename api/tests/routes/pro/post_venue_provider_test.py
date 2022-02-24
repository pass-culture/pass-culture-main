from unittest.mock import patch

import pytest

from pcapi.core.offers import factories as offer_factories
from pcapi.core.providers.api import activate_provider
import pcapi.core.providers.factories as providers_factories
from pcapi.core.providers.factories import AllocinePivotFactory
from pcapi.core.providers.models import VenueProvider
from pcapi.core.users import factories as user_factories
from pcapi.model_creators.generic_creators import create_venue_provider
from pcapi.models.api_errors import ApiErrors
from pcapi.repository import repository
from pcapi.utils.human_ids import dehumanize
from pcapi.utils.human_ids import humanize

from tests.conftest import TestClient
from tests.conftest import clean_database


class Returns201Test:
    @pytest.mark.usefixtures("db_session")
    @patch("pcapi.workers.venue_provider_job.venue_provider_job.delay")
    @patch("pcapi.core.providers.api._siret_can_be_synchronized")
    def when_venue_provider_is_successfully_created(
        self, mock_siret_can_be_synchronized, mock_synchronize_venue_provider, app
    ):
        # Given
        user = user_factories.AdminFactory()
        venue = offer_factories.VenueFactory(siret="12345678912345")

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
    def when_add_allocine_stocks_provider_with_price_but_no_isDuo_config(self, app):
        # Given
        venue = offer_factories.VenueFactory(managingOfferer__siren="775671464")
        user = user_factories.AdminFactory()
        AllocinePivotFactory(siret=venue.siret)

        provider = activate_provider("AllocineStocks")

        venue_provider_data = {"providerId": humanize(provider.id), "venueId": humanize(venue.id), "price": "9.99"}

        auth_request = TestClient(app.test_client()).with_session_auth(email=user.email)

        # When
        response = auth_request.post("/venueProviders", json=venue_provider_data)

        # Then
        assert response.status_code == 201
        json = response.json
        assert "_sa_polymorphic_on" not in json
        venue_provider = VenueProvider.query.one()
        assert json["venueId"] == humanize(venue_provider.venueId)

    @pytest.mark.usefixtures("db_session")
    def when_add_allocine_stocks_provider_with_default_settings_at_import(self, app):
        # Given
        venue = offer_factories.VenueFactory(managingOfferer__siren="775671464")
        user = user_factories.AdminFactory()
        AllocinePivotFactory(siret=venue.siret)

        provider = activate_provider("AllocineStocks")

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

    @pytest.mark.usefixtures("db_session")
    @patch("pcapi.workers.venue_provider_job.venue_provider_job.delay")
    @patch("pcapi.core.providers.api._siret_can_be_synchronized")
    def when_no_regression_on_format(self, mock_siret_can_be_synchronized, mock_synchronize_venue_provider, app):
        # Given
        user = user_factories.AdminFactory()
        venue = offer_factories.VenueFactory(siret="12345678912345")

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
    def when_venue_id_at_offer_provider_is_ignored_for_pro(
        self, mock_siret_can_be_synchronized, mock_synchronize_venue_provider, app
    ):
        # Given
        user = user_factories.AdminFactory()
        venue = offer_factories.VenueFactory(siret="12345678912345")

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
    @patch("pcapi.workers.venue_provider_job.venue_provider_job.delay")
    @patch("pcapi.core.providers.api._siret_can_be_synchronized")
    def test_when_add_same_provider(self, mock_siret_can_be_synchronized, mock_synchronize_venue_provider, app):
        # Given
        user = user_factories.AdminFactory()
        venue = offer_factories.VenueFactory(siret="12345678912345")
        provider = providers_factories.APIProviderFactory()
        venue_provider = create_venue_provider(venue, provider, venue_id_at_offer_provider="12345678912345")
        repository.save(venue_provider)

        auth_request = TestClient(app.test_client()).with_session_auth(email=user.email)
        venue_provider_data = {
            "providerId": humanize(provider.id),
            "venueId": humanize(venue.id),
        }
        mock_siret_can_be_synchronized.return_value = True

        # When
        response = auth_request.post("/venueProviders", json=venue_provider_data)

        # Then
        assert response.status_code == 400
        assert response.json == {"global": ["Votre lieu est déjà lié à cette source"]}
        assert venue.venueProviders[0].provider.id == provider.id


class Returns400Test:
    @pytest.mark.usefixtures("db_session")
    def when_api_error_raise_when_missing_fields(self, app):
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
    def when_add_allocine_stocks_provider_with_wrong_format_price(self, app):
        # Given
        venue = offer_factories.VenueFactory(managingOfferer__siren="775671464")
        user = user_factories.AdminFactory()
        AllocinePivotFactory(siret=venue.siret)

        provider = activate_provider("AllocineStocks")

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
    def when_add_allocine_stocks_provider_with_no_price(self, app):
        # Given
        venue = offer_factories.VenueFactory(managingOfferer__siren="775671464")
        user = user_factories.AdminFactory()
        AllocinePivotFactory(siret=venue.siret)

        provider = activate_provider("AllocineStocks")

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
    def when_user_is_not_logged_in(self, app):
        # when
        response = TestClient(app.test_client()).post("/venueProviders")

        # then
        assert response.status_code == 401


class Returns404Test:
    @pytest.mark.usefixtures("db_session")
    def when_venue_does_not_exist(self, app):
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
    def when_add_allocine_pivot_is_missing(self, app):
        # Given
        venue = offer_factories.VenueFactory(managingOfferer__siren="775671464")
        user = user_factories.AdminFactory()
        provider = activate_provider("AllocineStocks")

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
    def when_provider_api_not_available(self, mock_siret_can_be_synchronized, app):
        # Given
        user = user_factories.AdminFactory()
        venue = offer_factories.VenueFactory(siret="12345678912345")

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
    def should_inject_the_appropriate_repository_to_the_usecase(
        self, mocked_connect_venue_to_provider, mock_siret_can_be_synchronized, app
    ):
        # Given
        user = user_factories.AdminFactory()
        venue = offer_factories.VenueFactory(siret="12345678912345")

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
    def should_connect_to_allocine(
        self,
        app,
    ):
        # Given
        user = user_factories.AdminFactory()
        venue = offer_factories.VenueFactory(siret="12345678912345")
        AllocinePivotFactory(siret=venue.siret)

        provider = activate_provider("AllocineStocks")

        venue_provider_data = {"providerId": humanize(provider.id), "venueId": humanize(venue.id), "price": "33.33"}

        auth_request = TestClient(app.test_client()).with_session_auth(email=user.email)

        # When
        auth_request.post("/venueProviders", json=venue_provider_data)

        # Then
        assert len(venue.venueProviders) == 1
        assert venue.venueProviders[0].provider == provider
