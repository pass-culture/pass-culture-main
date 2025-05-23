from datetime import datetime
from unittest.mock import patch

import pytest

import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.providers.factories as providers_factories
import pcapi.core.providers.repository as providers_repository
from pcapi.connectors.serialization.cine_digital_service_serializers import IdObjectCDS
from pcapi.connectors.serialization.cine_digital_service_serializers import ShowCDS
from pcapi.connectors.serialization.cine_digital_service_serializers import ShowTariffCDS
from pcapi.connectors.serialization.cine_digital_service_serializers import ShowsMediaoptionsCDS
from pcapi.core.external_bookings.models import Movie
from pcapi.core.history import models as history_models
from pcapi.core.providers.factories import CinemaProviderPivotFactory
from pcapi.core.providers.models import Provider
from pcapi.core.providers.models import VenueProvider
from pcapi.core.users import factories as user_factories
from pcapi.models import db

from tests.local_providers.cinema_providers.cds import fixtures as cds_fixtures


class Returns201Test:
    @pytest.mark.usefixtures("db_session")
    @patch("pcapi.workers.venue_provider_job.venue_provider_job.delay")
    def test_when_venue_provider_is_successfully_created(self, mock_synchronize_venue_provider, client):
        # Given
        venue = offerers_factories.VenueFactory(siret="12345678912345")
        user = user_factories.ProFactory()
        offerers_factories.UserOffererFactory(user=user, offerer=venue.managingOfferer)

        provider = providers_factories.PublicApiProviderFactory()

        venue_provider_data = {
            "providerId": provider.id,
            "venueId": venue.id,
        }

        auth_request = client.with_session_auth(email=user.email)

        # When
        response = auth_request.post("/venueProviders", json=venue_provider_data)

        # Then
        assert response.status_code == 201
        venue_provider = db.session.query(VenueProvider).one()
        assert venue_provider.venueId == venue.id
        assert venue_provider.providerId == provider.id
        assert "id" in response.json
        action = db.session.query(history_models.ActionHistory).one()
        assert action.actionType == history_models.ActionType.SYNC_VENUE_TO_PROVIDER
        assert action.authorUser == user
        assert action.extraData["provider_name"] == venue_provider.provider.name

        mock_synchronize_venue_provider.assert_not_called()

    @pytest.mark.usefixtures("db_session")
    @patch("pcapi.workers.venue_provider_job.venue_provider_job.delay")
    def test_when_movie_provider_is_successfully_created(self, mock_synchronize_venue_provider, client):
        venue = offerers_factories.VenueFactory(siret="12345678912345")
        user = user_factories.ProFactory()
        offerers_factories.UserOffererFactory(user=user, offerer=venue.managingOfferer)
        provider = providers_factories.CGRCinemaProviderPivotFactory(venue=venue).provider

        venue_provider_data = {"providerId": provider.id, "venueId": venue.id}
        auth_request = client.with_session_auth(email=user.email)
        response = auth_request.post("/venueProviders", json=venue_provider_data)

        assert response.status_code == 201

        venue_provider_id = response.json["id"]
        mock_synchronize_venue_provider.assert_called_once_with(venue_provider_id)

    @pytest.mark.usefixtures("db_session")
    @patch("pcapi.workers.venue_provider_job.synchronize_venue_provider")
    def test_when_add_allocine_stocks_provider_with_default_settings_at_import(
        self, mock_synchronize_venue_provider, client
    ):
        # Given
        venue = offerers_factories.VenueFactory(managingOfferer__siren="775671464")
        user = user_factories.ProFactory()
        offerers_factories.UserOffererFactory(user=user, offerer=venue.managingOfferer)
        providers_factories.AllocineTheaterFactory(siret=venue.siret)
        provider = providers_factories.AllocineProviderFactory()

        venue_provider_data = {
            "providerId": provider.id,
            "venueId": venue.id,
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
        venue_provider = db.session.query(VenueProvider).one()
        mock_synchronize_venue_provider.assert_called_once_with(venue_provider)

    @pytest.mark.usefixtures("db_session")
    @patch("pcapi.workers.venue_provider_job.synchronize_venue_provider")
    def test_when_add_allocine_stocks_provider_for_venue_without_siret(self, mock_synchronize_venue_provider, client):
        # Given
        venue = offerers_factories.VenueWithoutSiretFactory(managingOfferer__siren="775671464")
        user = user_factories.ProFactory()
        offerers_factories.UserOffererFactory(user=user, offerer=venue.managingOfferer)
        providers_factories.AllocinePivotFactory(venue=venue)
        provider = providers_factories.AllocineProviderFactory()

        venue_provider_data = {
            "providerId": provider.id,
            "venueId": venue.id,
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
        venue_provider = db.session.query(VenueProvider).one()
        mock_synchronize_venue_provider.assert_called_once_with(venue_provider)

    @pytest.mark.usefixtures("db_session")
    @patch("pcapi.workers.venue_provider_job.venue_provider_job.delay")
    def test_when_no_regression_on_format(self, mock_synchronize_venue_provider, client):
        # Given
        venue = offerers_factories.VenueFactory(siret="12345678912345")
        user = user_factories.ProFactory()
        offerers_factories.UserOffererFactory(user=user, offerer=venue.managingOfferer)

        provider = providers_factories.PublicApiProviderFactory()

        venue_provider_data = {
            "providerId": provider.id,
            "venueId": venue.id,
        }

        auth_request = client.with_session_auth(email=user.email)

        # When
        response = auth_request.post("/venueProviders", json=venue_provider_data)

        # Then
        assert response.status_code == 201
        assert set(response.json.keys()) == {
            "dateCreated",
            "id",
            "isActive",
            "isDuo",
            "isFromAllocineProvider",
            "lastSyncDate",
            "price",
            "provider",
            "quantity",
            "venueId",
            "venueIdAtOfferProvider",
        }
        assert set(response.json["provider"].keys()) == {
            "id",
            "name",
            "isActive",
            "hasOffererProvider",
        }

    @pytest.mark.usefixtures("db_session")
    @patch("pcapi.workers.venue_provider_job.venue_provider_job.delay")
    def test_when_venue_id_at_offer_provider_is_ignored_for_pro(self, mock_synchronize_venue_provider, client):
        # Given
        venue = offerers_factories.VenueFactory(siret="12345678912345")
        user = user_factories.ProFactory()
        offerers_factories.UserOffererFactory(user=user, offerer=venue.managingOfferer)

        provider = providers_factories.PublicApiProviderFactory()

        venue_provider_data = {
            "providerId": provider.id,
            "venueId": venue.id,
            "venueIdAtOfferProvider": "====VY24G1AGF56",
        }

        auth_request = client.with_session_auth(email=user.email)

        # When
        response = auth_request.post("/venueProviders", json=venue_provider_data)

        # Then
        assert response.status_code == 201
        venue_provider = db.session.query(VenueProvider).one()
        assert venue_provider.venueId == venue.id
        assert venue_provider.providerId == provider.id
        assert "id" in response.json
        mock_synchronize_venue_provider.assert_not_called()

    @pytest.mark.usefixtures("db_session")
    def test_when_add_same_provider(self, client):
        # Given
        provider = providers_factories.PublicApiProviderFactory()
        venue_provider = providers_factories.VenueProviderFactory(provider=provider, venueIdAtOfferProvider=None)
        user = user_factories.ProFactory()
        offerers_factories.UserOffererFactory(user=user, offerer=venue_provider.venue.managingOfferer)

        client = client.with_session_auth(email=user.email)
        venue_provider_data = {
            "providerId": venue_provider.providerId,
            "venueId": venue_provider.venueId,
        }

        # When
        response = client.post("/venueProviders", json=venue_provider_data)

        # Then
        assert response.status_code == 400
        assert response.json == {"global": ["Votre lieu est déjà lié à cette source"]}
        assert venue_provider.venue.venueProviders == [venue_provider]

    @pytest.mark.usefixtures("db_session")
    @patch("pcapi.local_providers.cinema_providers.cds.cds_stocks.CDSStocks._get_cds_shows")
    @patch("pcapi.core.external_bookings.cds.client.CineDigitalServiceAPI.get_venue_movies")
    @patch("pcapi.settings.CDS_API_URL", "fakeUrl/")
    def test_create_venue_provider_for_cds_cinema(self, mock_get_venue_movies, mock_get_shows, requests_mock, client):
        # Given
        venue = offerers_factories.VenueFactory()
        user = user_factories.ProFactory()
        offerers_factories.UserOffererFactory(user=user, offerer=venue.managingOfferer)
        client = client.with_session_auth(email=user.email)
        provider = db.session.query(Provider).filter(Provider.localClass == "CDSStocks").first()

        cds_pivot = CinemaProviderPivotFactory(venue=venue, provider=provider)
        providers_factories.CDSCinemaDetailsFactory(
            cinemaProviderPivot=cds_pivot, cinemaApiToken="test_token", accountId="test_account"
        )

        venue_provider_data = {
            "providerId": provider.id,
            "venueId": venue.id,
            # TODO AMARINIER : add isDuo to payload when we implement cds modal
        }

        mocked_movies = [
            Movie(
                id="123",
                title="Coupez !",
                duration=120,
                description="Ca tourne mal",
                visa="123456",
                poster_url="fakeUrl/coupez.png",
            ),
            Movie(
                id="51",
                title="Top Gun",
                duration=150,
                description="Film sur les avions",
                visa="333333",
                poster_url="fakeUrl/topgun.png",
            ),
        ]
        mock_get_venue_movies.return_value = mocked_movies
        requests_mock.get(
            "https://test_account.fakeurl/cinemas?api_token=test_token",
            json=[cds_fixtures.CINEMA_WITH_INTERNET_SALE_GAUGE_ACTIVE_TRUE],
        )

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
                    shows_mediaoptions_collection=[ShowsMediaoptionsCDS(media_options_id=IdObjectCDS(id=12))],
                ),
                "price": 5,
                "price_label": "pass Culture",
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
                    shows_mediaoptions_collection=[ShowsMediaoptionsCDS(media_options_id=IdObjectCDS(id=12))],
                ),
                "price": 6,
                "price_label": "pass Culture",
            },
        ]
        mock_get_shows.return_value = mocked_shows

        response = client.post("/venueProviders", json=venue_provider_data)

        assert response.json["provider"]["id"] == provider.id
        assert response.json["venueId"] == venue.id
        assert response.json["venueIdAtOfferProvider"] == cds_pivot.idAtProvider

    @pytest.mark.usefixtures("db_session")
    @patch("pcapi.workers.venue_provider_job.synchronize_ems_venue_provider")
    def test_create_venue_provider_for_ems_cinema(self, mocked_synchronize_ems_venue_provider, requests_mock, client):
        venue = offerers_factories.VenueFactory()
        user = user_factories.ProFactory()
        offerers_factories.UserOffererFactory(user=user, offerer=venue.managingOfferer)
        ems_provider = providers_repository.get_provider_by_local_class("EMSStocks")
        pivot = providers_factories.CinemaProviderPivotFactory(venue=venue, provider=ems_provider)
        providers_factories.EMSCinemaDetailsFactory(cinemaProviderPivot=pivot)

        client = client.with_session_auth(email=user.email)
        venue_provider_data = {"providerId": ems_provider.id, "venueId": venue.id}

        response = client.post("/venueProviders", json=venue_provider_data)

        assert response.status_code == 201
        assert response.json["provider"]["id"] == ems_provider.id
        assert response.json["venueId"] == venue.id
        assert response.json["venueIdAtOfferProvider"] == pivot.idAtProvider
        venue_provider = db.session.query(VenueProvider).one()
        mocked_synchronize_ems_venue_provider.assert_called_once_with(venue_provider)
        venue_provider = db.session.query(VenueProvider).one()


class Returns400Test:
    @pytest.mark.usefixtures("db_session")
    def test_when_api_error_raise_when_missing_fields(self, client):
        # Given
        user = user_factories.ProFactory()
        auth_request = client.with_session_auth(email=user.email)
        venue_provider_data = {}

        # When
        response = auth_request.post("/venueProviders", json=venue_provider_data)

        # Then
        assert response.status_code == 400
        assert response.json["venueId"] == ["Ce champ est obligatoire"]
        assert response.json["providerId"] == ["Ce champ est obligatoire"]

    @pytest.mark.usefixtures("clean_database")
    def test_when_add_allocine_stocks_provider_with_wrong_format_price(self, client):
        # Given
        venue = offerers_factories.VenueFactory(managingOfferer__siren="775671464")
        user = user_factories.ProFactory()
        offerers_factories.UserOffererFactory(user=user, offerer=venue.managingOfferer)
        providers_factories.AllocineTheaterFactory(siret=venue.siret)
        provider = providers_factories.AllocineProviderFactory()

        venue_provider_data = {
            "providerId": provider.id,
            "venueId": venue.id,
            "isDuo": True,
            "price": "not a price",
        }

        auth_request = client.with_session_auth(email=user.email)

        # When
        response = auth_request.post("/venueProviders", json=venue_provider_data)

        # Then
        assert response.status_code == 400
        assert response.json == {"price": ["Saisissez un nombre valide"]}
        assert db.session.query(VenueProvider).count() == 0

    @pytest.mark.usefixtures("db_session")
    def test_when_add_allocine_stocks_provider_with_no_price(self, client):
        # Given
        venue = offerers_factories.VenueFactory(managingOfferer__siren="775671464")
        user = user_factories.ProFactory()
        offerers_factories.UserOffererFactory(user=user, offerer=venue.managingOfferer)
        providers_factories.AllocineTheaterFactory(siret=venue.siret)
        provider = providers_factories.AllocineProviderFactory()

        venue_provider_data = {
            "providerId": provider.id,
            "venueId": venue.id,
        }

        auth_request = client.with_session_auth(email=user.email)

        # When
        response = auth_request.post("/venueProviders", json=venue_provider_data)

        # Then
        assert response.status_code == 400
        assert response.json["price"] == ["Il est obligatoire de saisir un prix."]
        assert db.session.query(VenueProvider).count() == 0

    @pytest.mark.usefixtures("db_session")
    def test_when_add_allocine_stocks_provider_with_negative_price(self, client):
        # Given
        venue = offerers_factories.VenueFactory(managingOfferer__siren="775671464")
        user = user_factories.ProFactory()
        offerers_factories.UserOffererFactory(user=user, offerer=venue.managingOfferer)
        providers_factories.AllocineTheaterFactory(siret=venue.siret)
        provider = providers_factories.AllocineProviderFactory()

        venue_provider_data = {
            "providerId": provider.id,
            "venueId": venue.id,
            "price": -20,
        }

        auth_request = client.with_session_auth(email=user.email)

        # When
        response = auth_request.post("/venueProviders", json=venue_provider_data)

        # Then
        assert response.status_code == 400
        assert response.json["price"] == ["Le prix doit être positif."]
        assert db.session.query(VenueProvider).count() == 0


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
        user = user_factories.ProFactory()

        provider = providers_factories.PublicApiProviderFactory()

        venue_provider_data = {
            "providerId": provider.id,
            "venueId": "1234",
            "isDuo": False,
            "price": "9.99",
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
        user = user_factories.ProFactory()
        offerers_factories.UserOffererFactory(user=user, offerer=venue.managingOfferer)
        provider = providers_factories.AllocineProviderFactory()

        venue_provider_data = {
            "providerId": provider.id,
            "venueId": venue.id,
            "isDuo": False,
            "price": "9.99",
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
        assert db.session.query(VenueProvider).count() == 0


class ConnectProviderToVenueTest:
    @pytest.mark.usefixtures("db_session")
    @patch("pcapi.core.providers.api.connect_venue_to_provider")
    def test_should_inject_the_appropriate_repository_to_the_usecase(self, mocked_connect_venue_to_provider, client):
        # Given
        venue = offerers_factories.VenueFactory(siret="12345678912345")
        user = user_factories.ProFactory()
        offerers_factories.UserOffererFactory(user=user, offerer=venue.managingOfferer)

        provider = providers_factories.PublicApiProviderFactory()

        venue_provider_data = {
            "providerId": provider.id,
            "venueId": venue.id,
        }

        auth_request = client.with_session_auth(email=user.email)

        # When
        auth_request.post("/venueProviders", json=venue_provider_data)

        # Then
        mocked_connect_venue_to_provider.assert_called_once_with(venue, provider)

    @pytest.mark.usefixtures("db_session")
    @patch("pcapi.workers.venue_provider_job.venue_provider_job")
    def test_should_connect_to_allocine(
        self,
        mocked_venue_provider_job,
        client,
    ):
        # Given
        venue = offerers_factories.VenueFactory()
        user = user_factories.ProFactory()
        offerers_factories.UserOffererFactory(user=user, offerer=venue.managingOfferer)
        providers_factories.AllocineTheaterFactory(siret=venue.siret)
        provider = providers_factories.AllocineProviderFactory()

        venue_provider_data = {
            "providerId": provider.id,
            "venueId": venue.id,
            "price": "33.33",
            "isDuo": True,
        }

        auth_request = client.with_session_auth(email=user.email)

        # When
        auth_request.post("/venueProviders", json=venue_provider_data)

        # Then
        assert len(venue.venueProviders) == 1
        venue_provider = venue.venueProviders[0]
        assert venue_provider.provider == provider
        mocked_venue_provider_job.assert_called_once_with(venue_provider.id)

    @pytest.mark.usefixtures("db_session")
    @patch("pcapi.workers.venue_provider_job.venue_provider_job")
    def test_should_connect_to_provider_linked_to_an_offerer(
        self,
        mocked_venue_provider_job,
        client,
    ):
        venue = offerers_factories.VenueFactory()
        user = user_factories.ProFactory()
        offerers_factories.UserOffererFactory(user=user, offerer=venue.managingOfferer)
        provider = providers_factories.ProviderFactory(
            name="Technical provider", localClass=None, isActive=True, enabledForPro=True
        )
        providers_factories.OffererProviderFactory(offerer=venue.managingOfferer, provider=provider)

        venue_provider_data = {
            "providerId": provider.id,
            "venueId": venue.id,
        }

        response = client.with_session_auth(email=user.email).post("/venueProviders", json=venue_provider_data)

        assert response.status_code == 201
        assert len(venue.venueProviders) == 1
        venue_provider = venue.venueProviders[0]
        assert venue_provider.provider == provider
        mocked_venue_provider_job.assert_not_called()

    @pytest.mark.usefixtures("db_session")
    @patch("pcapi.workers.venue_provider_job.venue_provider_job")
    def test_should_connect_venue_without_siret_to_provider(
        self,
        mocked_venue_provider_job,
        client,
    ):
        venue = offerers_factories.VenueWithoutSiretFactory()
        user = user_factories.ProFactory()
        offerers_factories.UserOffererFactory(user=user, offerer=venue.managingOfferer)
        provider = providers_factories.ProviderFactory(
            name="Technical provider", localClass=None, isActive=True, enabledForPro=True
        )
        providers_factories.OffererProviderFactory(offerer=venue.managingOfferer, provider=provider)

        venue_provider_data = {
            "providerId": provider.id,
            "venueId": venue.id,
        }

        response = client.with_session_auth(email=user.email).post("/venueProviders", json=venue_provider_data)

        assert response.status_code == 201
        assert len(venue.venueProviders) == 1
        venue_provider = venue.venueProviders[0]
        assert venue_provider.provider == provider
        mocked_venue_provider_job.assert_not_called()
