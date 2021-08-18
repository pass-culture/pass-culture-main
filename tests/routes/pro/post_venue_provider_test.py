from unittest.mock import patch

import pytest

from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offers import factories as offer_factories
from pcapi.core.providers.factories import AllocinePivotFactory
from pcapi.core.providers.models import VenueProvider
from pcapi.core.users import factories as user_factories
from pcapi.model_creators.generic_creators import create_venue_provider
from pcapi.model_creators.provider_creators import activate_provider
from pcapi.models import ApiErrors
from pcapi.repository import repository
from pcapi.routes.serialization.venue_provider_serialize import PostVenueProviderBody
from pcapi.utils.human_ids import dehumanize
from pcapi.utils.human_ids import humanize

from tests.conftest import TestClient
from tests.conftest import clean_database


class Returns201Test:
    @pytest.mark.usefixtures("db_session")
    @patch("pcapi.workers.venue_provider_job.venue_provider_job.delay")
    @patch("pcapi.core.providers.api._check_venue_can_be_synchronized_with_provider")
    def when_venue_provider_is_successfully_created(self, stubbed_check, mock_synchronize_venue_provider, app):
        # Given
        user = user_factories.AdminFactory()
        venue = offer_factories.VenueFactory(siret="12345678912345")

        provider = offerers_factories.APIProviderFactory()

        venue_provider_data = {
            "providerId": humanize(provider.id),
            "venueId": humanize(venue.id),
        }

        auth_request = TestClient(app.test_client()).with_auth(email=user.email)
        stubbed_check.return_value = True

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

        auth_request = TestClient(app.test_client()).with_auth(email=user.email)

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
            "available": 50,
            "isDuo": True,
        }

        auth_request = TestClient(app.test_client()).with_auth(email=user.email)

        # When
        response = auth_request.post("/venueProviders", json=venue_provider_data)

        # Then
        assert response.status_code == 201
        assert response.json["price"] == 9.99

    @pytest.mark.usefixtures("db_session")
    @patch("pcapi.workers.venue_provider_job.venue_provider_job.delay")
    @patch("pcapi.core.providers.api._check_venue_can_be_synchronized_with_provider")
    def when_no_regression_on_format(self, stubbed_check, mock_synchronize_venue_provider, app):
        # Given
        user = user_factories.AdminFactory()
        venue = offer_factories.VenueFactory(siret="12345678912345")

        provider = offerers_factories.APIProviderFactory()

        venue_provider_data = {
            "providerId": humanize(provider.id),
            "venueId": humanize(venue.id),
        }

        auth_request = TestClient(app.test_client()).with_auth(email=user.email)
        stubbed_check.return_value = True

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
    @patch("pcapi.core.providers.api._check_venue_can_be_synchronized_with_provider")
    def when_venue_id_at_offer_provider_is_ignored_for_pro(self, stubbed_check, mock_synchronize_venue_provider, app):
        # Given
        user = user_factories.AdminFactory()
        venue = offer_factories.VenueFactory(siret="12345678912345")

        provider = offerers_factories.APIProviderFactory()

        venue_provider_data = {
            "providerId": humanize(provider.id),
            "venueId": humanize(venue.id),
            "venueIdAtOfferProvider": "====VY24G1AGF56",
        }

        auth_request = TestClient(app.test_client()).with_auth(email=user.email)
        stubbed_check.return_value = True

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


class Returns400Test:
    @pytest.mark.usefixtures("db_session")
    def when_api_error_raise_when_missing_fields(self, app):
        # Given
        user = user_factories.AdminFactory()
        auth_request = TestClient(app.test_client()).with_auth(email=user.email)
        venue_provider_data = {}

        # When
        response = auth_request.post("/venueProviders", json=venue_provider_data)

        # Then
        assert response.status_code == 400
        assert response.json["venueId"] == ["Ce champ est obligatoire"]
        assert response.json["providerId"] == ["Ce champ est obligatoire"]

    @pytest.mark.usefixtures("db_session")
    @patch("pcapi.core.providers.api._check_venue_can_be_synchronized_with_provider")
    def when_trying_to_add_existing_provider(self, stubbed_check, app):
        # Given
        user = user_factories.AdminFactory()
        venue = offer_factories.VenueFactory(siret="12345678912345")
        provider = offerers_factories.APIProviderFactory()
        venue_provider = create_venue_provider(venue, provider, venue_id_at_offer_provider="12345678912345")
        repository.save(venue_provider)

        auth_request = TestClient(app.test_client()).with_auth(email=user.email)
        venue_provider_data = {
            "providerId": humanize(provider.id),
            "venueId": humanize(venue.id),
        }
        stubbed_check.return_value = True

        # When
        response = auth_request.post("/venueProviders", json=venue_provider_data)

        # Then
        assert response.status_code == 400
        assert response.json["global"] == ["Votre lieu est déjà lié à cette source"]

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

        auth_request = TestClient(app.test_client()).with_auth(email=user.email)

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

        auth_request = TestClient(app.test_client()).with_auth(email=user.email)

        # When
        response = auth_request.post("/venueProviders", json=venue_provider_data)

        # Then
        assert response.status_code == 400
        assert response.json["price"] == ["Cette information est obligatoire"]
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

        provider = offerers_factories.APIProviderFactory()

        venue_provider_data = {
            "providerId": humanize(provider.id),
            "venueId": "AZERT",
        }

        auth_request = TestClient(app.test_client()).with_auth(email=user.email)

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

        auth_request = TestClient(app.test_client()).with_auth(email=user.email)

        # When
        response = auth_request.post("/venueProviders", json=venue_provider_data)

        # Then
        assert response.status_code == 404
        assert response.json == {"global": ["No Allocine pivot was found for this venue"]}
        assert VenueProvider.query.count() == 0


class Returns422Test:
    @pytest.mark.usefixtures("db_session")
    @patch("pcapi.core.providers.api._check_venue_can_be_synchronized_with_provider")
    def when_provider_api_not_available(self, stubbed_check, app):
        # Given
        user = user_factories.AdminFactory()
        venue = offer_factories.VenueFactory(siret="12345678912345")

        provider = offerers_factories.APIProviderFactory()

        venue_provider_data = {
            "providerId": humanize(provider.id),
            "venueId": humanize(venue.id),
        }

        auth_request = TestClient(app.test_client()).with_auth(email=user.email)

        errors = ApiErrors()
        errors.status_code = 422
        errors.add_error(
            "provider",
            "L’importation d’offres avec LesLibraires n’est pas disponible " "pour le SIRET 12345678912345",
        )
        stubbed_check.side_effect = [errors]

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
    @patch("pcapi.core.providers.api._check_venue_can_be_synchronized_with_provider")
    @patch("pcapi.core.providers.api.connect_venue_to_provider")
    def should_inject_the_appropriate_repository_to_the_usecase(
        self, mocked_connect_venue_to_provider, stubbed_check, app
    ):
        # Given
        user = user_factories.AdminFactory()
        venue = offer_factories.VenueFactory(siret="12345678912345")

        provider = offerers_factories.APIProviderFactory()

        venue_provider_data = {
            "providerId": humanize(provider.id),
            "venueId": humanize(venue.id),
        }

        auth_request = TestClient(app.test_client()).with_auth(email=user.email)
        stubbed_check.return_value = True

        # When
        auth_request.post("/venueProviders", json=venue_provider_data)

        # Then
        mocked_connect_venue_to_provider.assert_called_once_with(venue, provider, None)

    @pytest.mark.usefixtures("db_session")
    @patch("pcapi.core.providers.api._check_venue_can_be_synchronized_with_provider")
    @patch("pcapi.core.providers.api.connect_venue_to_allocine")
    def should_inject_no_repository_to_the_usecase_when_provider_is_not_concerned(
        self,
        mocked_connect_venue_to_allocine,
        stubbed_check,
        app,
    ):
        # Given
        user = user_factories.AdminFactory()
        venue = offer_factories.VenueFactory(siret="12345678912345")
        AllocinePivotFactory(siret=venue.siret)

        provider = activate_provider("AllocineStocks")

        venue_provider_data = {
            "providerId": humanize(provider.id),
            "venueId": humanize(venue.id),
        }

        auth_request = TestClient(app.test_client()).with_auth(email=user.email)
        stubbed_check.return_value = True

        # When
        auth_request.post("/venueProviders", json=venue_provider_data)

        # Then
        mocked_connect_venue_to_allocine.assert_called_once_with(
            venue, PostVenueProviderBody(providerId=humanize(provider.id), venueId=humanize(venue.id))
        )
