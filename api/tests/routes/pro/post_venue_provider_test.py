from datetime import datetime
from unittest.mock import patch

import pytest

from pcapi.connectors.serialization.cine_digital_service_serializers import IdObjectCDS
from pcapi.connectors.serialization.cine_digital_service_serializers import ShowCDS
from pcapi.connectors.serialization.cine_digital_service_serializers import ShowTariffCDS
from pcapi.core.booking_providers.models import Movie
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.providers.factories as providers_factories
from pcapi.core.providers.factories import CinemaProviderPivotFactory
from pcapi.core.providers.models import Provider
from pcapi.core.providers.models import VenueProvider
from pcapi.core.users import factories as user_factories
from pcapi.models.api_errors import ApiErrors
from pcapi.utils.human_ids import dehumanize
from pcapi.utils.human_ids import humanize

from tests.conftest import clean_database


class Returns201Test:
    @pytest.mark.usefixtures("db_session")
    @patch("pcapi.workers.venue_provider_job.venue_provider_job.delay")
    @patch("pcapi.core.providers.api._siret_can_be_synchronized")
    def test_when_venue_provider_is_successfully_created(
        self, mock_siret_can_be_synchronized, mock_synchronize_venue_provider, client
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

        auth_request = client.with_session_auth(email=user.email)

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
    def test_when_add_allocine_stocks_provider_with_default_settings_at_import(
        self, mock_synchronize_venue_provider, client
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

        auth_request = client.with_session_auth(email=user.email)

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
    @patch("pcapi.workers.venue_provider_job.synchronize_venue_provider")
    def test_when_add_allocine_stocks_provider_for_venue_without_siret(self, mock_synchronize_venue_provider, client):
        # Given
        venue = offerers_factories.VenueFactory(managingOfferer__siren="775671464", siret=None, comment="some comment")
        user = user_factories.AdminFactory()
        providers_factories.AllocinePivotFactory(venue=venue)
        provider = providers_factories.AllocineProviderFactory()

        venue_provider_data = {
            "providerId": humanize(provider.id),
            "venueId": humanize(venue.id),
            "price": "9.99",
            "quantity": 50,
            "isDuo": True,
        }

        auth_request = client.with_session_auth(email=user.email)

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
    def test_when_no_regression_on_format(
        self, mock_siret_can_be_synchronized, mock_synchronize_venue_provider, client
    ):
        # Given
        user = user_factories.AdminFactory()
        venue = offerers_factories.VenueFactory(siret="12345678912345")

        provider = providers_factories.APIProviderFactory()

        venue_provider_data = {
            "providerId": humanize(provider.id),
            "venueId": humanize(venue.id),
        }

        auth_request = client.with_session_auth(email=user.email)
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
        self, mock_siret_can_be_synchronized, mock_synchronize_venue_provider, client
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

        auth_request = client.with_session_auth(email=user.email)
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
    @patch(
        "pcapi.local_providers.cinema_providers.cds.cds_stocks.CDSStocks._get_cds_internet_sale_gauge",
        lambda *args: True,
    )
    @patch("pcapi.local_providers.cinema_providers.cds.cds_stocks.CDSStocks._get_cds_shows")
    @patch("pcapi.core.booking_providers.cds.client.CineDigitalServiceAPI.get_venue_movies")
    @patch("pcapi.settings.CDS_API_URL", "fakeUrl")
    def test_create_venue_provider_for_cds_cinema(self, mock_get_venue_movies, mock_get_shows, client):
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

        mocked_movies = [
            Movie(
                id="123",
                title="Coupez !",
                duration=120,
                description="Ca tourne mal",
                visa="123456",
                posterpath="fakeUrl/coupez.png",
            ),
            Movie(
                id="51",
                title="Top Gun",
                duration=150,
                description="Film sur les avions",
                visa="333333",
                posterpath="fakeUrl/topgun.png",
            ),
        ]
        mock_get_venue_movies.return_value = mocked_movies

        mocked_shows = [
            {
                "show_information": ShowCDS(
                    id=1,
                    is_cancelled=False,
                    is_deleted=False,
                    is_disabled_seatmap=False,
                    is_empty_seatmap=False,
                    remaining_place=77,
                    internet_remaining_place=10,
                    showtime=datetime(2022, 6, 20, 11, 00, 00),
                    shows_tariff_pos_type_collection=[ShowTariffCDS(tariff=IdObjectCDS(id=4))],
                    screen=IdObjectCDS(id=1),
                    media=IdObjectCDS(id=123),
                ),
                "price": 5,
            },
            {
                "show_information": ShowCDS(
                    id=2,
                    is_cancelled=False,
                    is_deleted=False,
                    is_disabled_seatmap=False,
                    is_empty_seatmap=False,
                    remaining_place=78,
                    internet_remaining_place=11,
                    showtime=datetime(2022, 7, 1, 12, 00, 00),
                    shows_tariff_pos_type_collection=[ShowTariffCDS(tariff=IdObjectCDS(id=4))],
                    screen=IdObjectCDS(id=1),
                    media=IdObjectCDS(id=51),
                ),
                "price": 6,
            },
        ]
        mock_get_shows.return_value = mocked_shows

        # When
        response = client.post("/venueProviders", json=venue_provider_data)

        # Then
        assert response.json["nOffers"] == 2
        assert response.json["providerId"] == humanize(provider.id)
        assert response.json["venueId"] == humanize(venue.id)
        assert response.json["venueIdAtOfferProvider"] == cds_pivot.idAtProvider


class Returns400Test:
    @pytest.mark.usefixtures("db_session")
    def test_when_api_error_raise_when_missing_fields(self, client):
        # Given
        user = user_factories.AdminFactory()
        auth_request = client.with_session_auth(email=user.email)
        venue_provider_data = {}

        # When
        response = auth_request.post("/venueProviders", json=venue_provider_data)

        # Then
        assert response.status_code == 400
        assert response.json["venueId"] == ["Ce champ est obligatoire"]
        assert response.json["providerId"] == ["Ce champ est obligatoire"]

    @clean_database
    def test_when_add_allocine_stocks_provider_with_wrong_format_price(self, client):
        # Given
        venue = offerers_factories.VenueFactory(managingOfferer__siren="775671464")
        user = user_factories.AdminFactory()
        providers_factories.AllocineTheaterFactory(siret=venue.siret)
        provider = providers_factories.AllocineProviderFactory()

        venue_provider_data = {
            "providerId": humanize(provider.id),
            "venueId": humanize(venue.id),
            "isDuo": True,
            "price": "wrong_price",
        }

        auth_request = client.with_session_auth(email=user.email)

        # When
        response = auth_request.post("/venueProviders", json=venue_provider_data)

        # Then
        assert response.status_code == 400
        assert response.json["global"] == ["Le prix doit être un nombre décimal"]
        assert VenueProvider.query.count() == 0

    @pytest.mark.usefixtures("db_session")
    def test_when_add_allocine_stocks_provider_with_no_price(self, client):
        # Given
        venue = offerers_factories.VenueFactory(managingOfferer__siren="775671464")
        user = user_factories.AdminFactory()
        providers_factories.AllocineTheaterFactory(siret=venue.siret)
        provider = providers_factories.AllocineProviderFactory()

        venue_provider_data = {
            "providerId": humanize(provider.id),
            "venueId": humanize(venue.id),
        }

        auth_request = client.with_session_auth(email=user.email)

        # When
        response = auth_request.post("/venueProviders", json=venue_provider_data)

        # Then
        assert response.status_code == 400
        assert response.json["price"] == ["Il est obligatoire de saisir un prix."]
        assert VenueProvider.query.count() == 0


class Returns401Test:
    @pytest.mark.usefixtures("db_session")
    def test_when_user_is_not_logged_in(self, client):
        # when
        response = client.post("/venueProviders")

        # then
        assert response.status_code == 401


class Returns404Test:
    @pytest.mark.usefixtures("db_session")
    def test_when_venue_does_not_exist(self, client):
        # Given
        user = user_factories.AdminFactory()

        provider = providers_factories.APIProviderFactory()

        venue_provider_data = {
            "providerId": humanize(provider.id),
            "venueId": "AZERT",
        }

        auth_request = client.with_session_auth(email=user.email)

        # When
        response = auth_request.post("/venueProviders", json=venue_provider_data)

        # Then
        assert response.status_code == 404

    @pytest.mark.usefixtures("db_session")
    def test_when_add_allocine_pivot_is_missing(self, client):
        # Given
        venue = offerers_factories.VenueFactory(managingOfferer__siren="775671464")
        user = user_factories.AdminFactory()
        provider = providers_factories.AllocineProviderFactory()

        venue_provider_data = {
            "providerId": humanize(provider.id),
            "venueId": humanize(venue.id),
        }

        auth_request = client.with_session_auth(email=user.email)

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
    def test_when_provider_api_not_available(self, mock_siret_can_be_synchronized, client):
        # Given
        user = user_factories.AdminFactory()
        venue = offerers_factories.VenueFactory(siret="12345678912345")

        provider = providers_factories.APIProviderFactory()

        venue_provider_data = {
            "providerId": humanize(provider.id),
            "venueId": humanize(venue.id),
        }

        auth_request = client.with_session_auth(email=user.email)

        errors = ApiErrors()
        errors.status_code = 422
        errors.add_error(
            "provider",
            "L’importation d’offres avec LesLibraires n’est pas disponible pour le SIRET 12345678912345",
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
        self, mocked_connect_venue_to_provider, mock_siret_can_be_synchronized, client
    ):
        # Given
        user = user_factories.AdminFactory()
        venue = offerers_factories.VenueFactory(siret="12345678912345")

        provider = providers_factories.APIProviderFactory()

        venue_provider_data = {
            "providerId": humanize(provider.id),
            "venueId": humanize(venue.id),
        }

        auth_request = client.with_session_auth(email=user.email)
        mock_siret_can_be_synchronized.return_value = True

        # When
        auth_request.post("/venueProviders", json=venue_provider_data)

        # Then
        mocked_connect_venue_to_provider.assert_called_once_with(venue, provider, None)

    @pytest.mark.usefixtures("db_session")
    def test_should_connect_to_allocine(
        self,
        client,
    ):
        # Given
        user = user_factories.AdminFactory()
        venue = offerers_factories.VenueFactory()
        providers_factories.AllocineTheaterFactory(siret=venue.siret)
        provider = providers_factories.AllocineProviderFactory()

        venue_provider_data = {
            "providerId": humanize(provider.id),
            "venueId": humanize(venue.id),
            "price": "33.33",
            "isDuo": True,
        }

        auth_request = client.with_session_auth(email=user.email)

        # When
        auth_request.post("/venueProviders", json=venue_provider_data)

        # Then
        assert len(venue.venueProviders) == 1
        assert venue.venueProviders[0].provider == provider
