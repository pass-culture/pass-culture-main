from datetime import datetime
from datetime import timedelta
from unittest import mock
from unittest.mock import patch

import pytest
import time_machine

from pcapi import settings
import pcapi.core.artist.factories as artists_factories
from pcapi.core.artist.models import ArtistType
from pcapi.core.bookings.factories import BookingFactory
from pcapi.core.categories import app_search_tree
from pcapi.core.categories import models as categories_models
from pcapi.core.categories import subcategories
import pcapi.core.chronicles.factories as chronicles_factories
from pcapi.core.geography.factories import AddressFactory
import pcapi.core.mails.testing as mails_testing
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offerers.factories import OffererAddressFactory
from pcapi.core.offerers.factories import VenueFactory
import pcapi.core.offers.factories as offers_factories
from pcapi.core.offers.models import OfferReport
from pcapi.core.offers.models import TiteliveImageType
from pcapi.core.providers.constants import BookFormat
import pcapi.core.providers.factories as providers_factories
from pcapi.core.providers.repository import get_provider_by_local_class
from pcapi.core.reactions.factories import ReactionFactory
from pcapi.core.reactions.models import ReactionTypeEnum
from pcapi.core.testing import assert_no_duplicated_queries
from pcapi.core.testing import assert_num_queries
from pcapi.core.users import factories as users_factories
from pcapi.core.users.factories import UserFactory
import pcapi.local_providers.cinema_providers.constants as cinema_providers_constants
from pcapi.models.offer_mixin import OfferValidationStatus
import pcapi.notifications.push.testing as notifications_testing
from pcapi.routes.native.v1.serialization.offers import MAX_PREVIEW_CHRONICLES
from pcapi.utils import date as date_utils

from tests.connectors.cgr import soap_definitions
from tests.local_providers.cinema_providers.boost import fixtures as boost_fixtures
from tests.local_providers.cinema_providers.cgr import fixtures as cgr_fixtures


pytestmark = pytest.mark.usefixtures("db_session")


class OffersTest:
    @time_machine.travel("2020-01-01", tick=False)
    def test_get_event_offer(self, client):
        extra_data = {
            "allocineId": 12345,
            "author": "mandibule",
            "ean": "3838",
            "musicSubType": "502",
            "musicType": "501",
            "performer": "interprète",
            "showSubType": "101",
            "showType": "100",
            "stageDirector": "metteur en scène",
            "speaker": "intervenant",
            "visa": "vasi",
            "genres": ["ACTION", "DRAMA"],
            "cast": ["cast1", "cast2"],
            "editeur": "editeur",
            "gtl_id": "01030000",
            "releaseDate": "2020-01-01",
            "certificate": "Interdit au moins de 18 ans",
        }
        offer = offers_factories.OfferFactory(
            subcategoryId=subcategories.SEANCE_CINE.id,
            isDuo=True,
            description="desk cryption",
            name="l'offre du siècle",
            withdrawalDetails="modalité de retrait",
            extraData=extra_data,
            durationMinutes=33,
            visualDisabilityCompliant=True,
            externalTicketOfficeUrl="https://url.com",
            venue__name="il est venu le temps des names",
        )
        offers_factories.MediationFactory(id=111, offer=offer, thumbCount=1, credit="street credit")

        bookable_stock = offers_factories.EventStockFactory(
            offer=offer,
            price=12.34,
            quantity=2,
            priceCategory__priceCategoryLabel__label="bookable",
            features=[
                cinema_providers_constants.ShowtimeFeatures.VF.value,
                cinema_providers_constants.ShowtimeFeatures.THREE_D.value,
                cinema_providers_constants.ShowtimeFeatures.ICE.value,
            ],
        )
        another_bookable_stock = offers_factories.EventStockFactory(
            offer=offer,
            price=12.34,
            quantity=3,
            priceCategory=bookable_stock.priceCategory,
            features=[
                cinema_providers_constants.ShowtimeFeatures.VO.value,
                cinema_providers_constants.ShowtimeFeatures.THREE_D.value,
            ],
        )
        expired_stock = offers_factories.EventStockFactory(
            offer=offer,
            price=45.67,
            beginningDatetime=datetime.utcnow() - timedelta(days=1),
            priceCategory__priceCategoryLabel__label="expired",
            features=[
                cinema_providers_constants.ShowtimeFeatures.VF.value,
                cinema_providers_constants.ShowtimeFeatures.ICE.value,
            ],
        )
        exhausted_stock = offers_factories.EventStockFactory(
            offer=offer,
            price=89.00,
            quantity=1,
            priceCategory__priceCategoryLabel__label="exhausted",
            features=[cinema_providers_constants.ShowtimeFeatures.VO.value],
        )

        BookingFactory(stock=bookable_stock, user__deposit__expirationDate=datetime(year=2031, month=12, day=31))
        BookingFactory(stock=exhausted_stock, user__deposit__expirationDate=datetime(year=2031, month=12, day=31))
        offer_id = offer.id

        nb_queries = 1  # select offer
        nb_queries += 1  # select stocks
        nb_queries += 1  # select mediations
        nb_queries += 1  # select chronicles
        nb_queries += 1  # select futureOffer
        with assert_num_queries(nb_queries):
            with assert_no_duplicated_queries():
                response = client.get(f"/native/v1/offer/{offer_id}")
                assert response.status_code == 200

        assert response.json["id"] == offer.id
        assert response.json["accessibility"] == {
            "audioDisability": False,
            "mentalDisability": False,
            "motorDisability": False,
            "visualDisability": True,
        }
        assert sorted(response.json["stocks"], key=lambda stock: stock["id"]) == sorted(
            [
                {
                    "id": bookable_stock.id,
                    "price": 1234,
                    "beginningDatetime": "2020-01-31T00:00:00Z",
                    "bookingLimitDatetime": "2020-01-30T23:00:00Z",
                    "cancellationLimitDatetime": "2020-01-03T00:00:00Z",
                    "features": ["VF", "3D", "ICE"],
                    "isBookable": True,
                    "isForbiddenToUnderage": False,
                    "isSoldOut": False,
                    "isExpired": False,
                    "activationCode": None,
                    "priceCategoryLabel": "bookable",
                    "remainingQuantity": 1,
                },
                {
                    "id": another_bookable_stock.id,
                    "price": 1234,
                    "beginningDatetime": "2020-01-31T00:00:00Z",
                    "bookingLimitDatetime": "2020-01-30T23:00:00Z",
                    "cancellationLimitDatetime": "2020-01-03T00:00:00Z",
                    "features": ["VO", "3D"],
                    "isBookable": True,
                    "isForbiddenToUnderage": False,
                    "isSoldOut": False,
                    "isExpired": False,
                    "activationCode": None,
                    "priceCategoryLabel": "bookable",
                    "remainingQuantity": 3,
                },
                {
                    "id": expired_stock.id,
                    "price": 4567,
                    "beginningDatetime": "2019-12-31T00:00:00Z",
                    "bookingLimitDatetime": "2019-12-30T23:00:00Z",
                    "cancellationLimitDatetime": "2020-01-01T00:00:00Z",
                    "features": ["VF", "ICE"],
                    "isBookable": False,
                    "isForbiddenToUnderage": False,
                    "isSoldOut": True,
                    "isExpired": True,
                    "activationCode": None,
                    "priceCategoryLabel": "expired",
                    "remainingQuantity": 1000,
                },
                {
                    "id": exhausted_stock.id,
                    "price": 8900,
                    "beginningDatetime": "2020-01-31T00:00:00Z",
                    "bookingLimitDatetime": "2020-01-30T23:00:00Z",
                    "cancellationLimitDatetime": "2020-01-03T00:00:00Z",
                    "features": ["VO"],
                    "isBookable": False,
                    "isForbiddenToUnderage": False,
                    "isSoldOut": True,
                    "isExpired": False,
                    "activationCode": None,
                    "priceCategoryLabel": "exhausted",
                    "remainingQuantity": 0,
                },
            ],
            key=lambda stock: stock["id"],
        )
        assert response.json["description"] == "desk cryption"
        assert response.json["externalTicketOfficeUrl"] == "https://url.com"
        assert response.json["expenseDomains"] == ["all"]
        assert response.json["extraData"] == {
            "allocineId": 12345,
            "author": "mandibule",
            "ean": "3838",
            "durationMinutes": 33,
            "musicSubType": "Acid Jazz",
            "musicType": "Jazz",
            "performer": "interprète",
            "showSubType": "Carnaval",
            "showType": "Arts de la rue",
            "speaker": "intervenant",
            "stageDirector": "metteur en scène",
            "visa": "vasi",
            "genres": ["Action", "Drame"],
            "cast": ["cast1", "cast2"],
            "editeur": "editeur",
            "gtlLabels": {
                "label": "Œuvres classiques",
                "level01Label": "Littérature",
                "level02Label": "Œuvres classiques",
                "level03Label": None,
                "level04Label": None,
            },
            "releaseDate": "2020-01-01",
            "certificate": "Interdit au moins de 18 ans",
            "bookFormat": None,
        }
        assert response.json["image"] == {
            "url": "http://localhost/storage/thumbs/mediations/N4",
            "credit": "street credit",
        }
        assert response.json["isExpired"] is False
        assert response.json["isForbiddenToUnderage"] is False
        assert response.json["isSoldOut"] is False
        assert response.json["isDuo"] is True
        assert response.json["isEducational"] is False
        assert response.json["isDigital"] is False
        assert response.json["isReleased"] is True
        assert response.json["name"] == "l'offre du siècle"
        assert response.json["subcategoryId"] == subcategories.SEANCE_CINE.id
        assert response.json["venue"] == {
            "id": offer.venue.id,
            "address": "1 boulevard Poissonnière",
            "city": "Paris",
            "coordinates": {
                "latitude": 48.87004,
                "longitude": 2.3785,
            },
            "name": "il est venu le temps des names",
            "offerer": {"name": offer.venue.managingOfferer.name},
            "postalCode": "75002",
            "publicName": "il est venu le temps des names",
            "isPermanent": False,
            "isOpenToPublic": False,
            "timezone": "Europe/Paris",
            "bannerUrl": offer.venue.bannerUrl,
        }
        assert response.json["withdrawalDetails"] == "modalité de retrait"
        assert response.json["publicationDate"] is None

    def test_get_offer_with_unlimited_stock(self, client):
        product = offers_factories.ProductFactory(thumbCount=1)
        offer = offers_factories.OfferFactory(product=product, venue__isPermanent=True)
        offers_factories.ThingStockFactory(offer=offer, price=12.34, quantity=None)

        offer_id = offer.id
        # 1. select offer
        # 2. select stocks
        # 3. select mediations
        # 4. select chronicles
        # 5. select futureOffer
        # 6. select artists
        with assert_num_queries(6):
            with assert_no_duplicated_queries():
                response = client.get(f"/native/v1/offer/{offer_id}")
                assert response.status_code == 200

        assert response.json["stocks"][0]["remainingQuantity"] is None

    # FIXME : mageoffray (24-10-2024)
    # delete this test once None extraData has been fixed
    def test_get_offer_with_extra_data_as_none(self, client):
        offer = offers_factories.OfferFactory(extraData=None)
        offers_factories.ThingStockFactory(offer=offer, price=12.34, quantity=None)

        offer_id = offer.id
        nb_queries = 1  # select offer
        nb_queries += 1  # select stocks
        nb_queries += 1  # select mediations
        nb_queries += 1  # select chronicles
        nb_queries += 1  # select futureOffer
        with assert_num_queries(nb_queries):
            with assert_no_duplicated_queries():
                response = client.get(f"/native/v1/offer/{offer_id}")
                assert response.status_code == 200

    def test_get_thing_offer(self, client):
        offer = offers_factories.OfferFactory(venue__isPermanent=True, subcategoryId=subcategories.CARTE_MUSEE.id)
        offers_factories.ThingStockFactory(offer=offer, price=12.34)

        offer_id = offer.id
        nb_queries = 1  # select offer
        nb_queries += 1  # select stocks
        nb_queries += 1  # select mediations
        nb_queries += 1  # select chronicles
        nb_queries += 1  # select futureOffer
        with assert_num_queries(nb_queries):
            with assert_no_duplicated_queries():
                response = client.get(f"/native/v1/offer/{offer_id}")
                assert response.status_code == 200

        assert not response.json["stocks"][0]["beginningDatetime"]
        assert response.json["stocks"][0]["price"] == 1234
        assert response.json["stocks"][0]["priceCategoryLabel"] is None
        assert response.json["stocks"][0]["remainingQuantity"] == 1000
        assert response.json["subcategoryId"] == "CARTE_MUSEE"
        assert response.json["isEducational"] is False
        assert not response.json["isExpired"]
        assert response.json["venue"]["isPermanent"]
        assert response.json["stocks"][0]["features"] == []

    @pytest.mark.parametrize(
        "provider_class,ff_name,ff_value,booking_disabled",
        [
            ("EMSStocks", "DISABLE_EMS_EXTERNAL_BOOKINGS", True, True),
            ("EMSStocks", "DISABLE_EMS_EXTERNAL_BOOKINGS", False, False),
            ("CGRStocks", "DISABLE_CGR_EXTERNAL_BOOKINGS", True, True),
            ("CGRStocks", "DISABLE_CGR_EXTERNAL_BOOKINGS", False, False),
            ("CDSStocks", "DISABLE_CDS_EXTERNAL_BOOKINGS", True, True),
            ("CDSStocks", "DISABLE_CDS_EXTERNAL_BOOKINGS", False, False),
            ("BoostStocks", "DISABLE_BOOST_EXTERNAL_BOOKINGS", True, True),
            ("BoostStocks", "DISABLE_BOOST_EXTERNAL_BOOKINGS", False, False),
            ("BoostStocks", "DISABLE_EMS_EXTERNAL_BOOKINGS", True, False),
        ],
    )
    def test_offer_external_booking_is_disabled_by_ff(
        self, features, client, provider_class, ff_name, ff_value, booking_disabled
    ):
        provider = get_provider_by_local_class(provider_class)
        product = offers_factories.ProductFactory(thumbCount=1, subcategoryId=subcategories.SEANCE_CINE.id)
        offer = offers_factories.OfferFactory(
            product=product,
            venue__isPermanent=True,
            subcategoryId=subcategories.SEANCE_CINE.id,
            lastProvider=provider,
        )
        providers_factories.VenueProviderFactory(venue=offer.venue, provider=provider)

        offer_id = offer.id
        setattr(features, ff_name, ff_value)
        # 1. select offer
        # 2. select stocks
        # 3. select mediations
        # 4. check cinema venue_provider exists
        # 5. select active cinema provider
        # 6. check offer is from current cinema provider
        # 7. update offer (deactivate)
        # 8. select feature
        # 9. select chronicles
        # 10. select futureOffer
        # 11. select artists
        with assert_num_queries(11):
            with assert_no_duplicated_queries():
                response = client.get(f"/native/v1/offer/{offer_id}")
                assert response.status_code == 200

        assert response.json["isExternalBookingsDisabled"] is booking_disabled

    def test_get_digital_offer_with_available_activation_and_no_expiration_date(self, client):
        stock = offers_factories.StockWithActivationCodesFactory()
        offer_id = stock.offer.id

        nb_queries = 1  # select offer
        nb_queries += 1  # select stocks
        nb_queries += 1  # select mediations
        nb_queries += 1  # select activation_code
        nb_queries += 1  # select chronicles
        nb_queries += 1  # select futureOffer
        with assert_num_queries(nb_queries):
            with assert_no_duplicated_queries():
                response = client.get(f"/native/v1/offer/{offer_id}")
                assert response.status_code == 200

        assert response.json["stocks"][0]["activationCode"] == {"expirationDate": None}

    def test_get_digital_offer_with_available_activation_code_and_expiration_date(self, client):
        stock = offers_factories.StockWithActivationCodesFactory(activationCodes__expirationDate=datetime(2050, 1, 1))
        offer_id = stock.offer.id

        nb_queries = 1  # select offer
        nb_queries += 1  # select stocks
        nb_queries += 1  # select mediations
        nb_queries += 1  # select activation_code
        nb_queries += 1  # select chronicles
        nb_queries += 1  # select futureOffer
        with assert_num_queries(nb_queries):
            with assert_no_duplicated_queries():
                response = client.get(f"/native/v1/offer/{offer_id}")
                assert response.status_code == 200

        assert response.json["stocks"][0]["activationCode"] == {"expirationDate": "2050-01-01T00:00:00Z"}

    def test_get_digital_offer_without_available_activation_code(self, client):
        stock = offers_factories.StockWithActivationCodesFactory(activationCodes__expirationDate=datetime(2000, 1, 1))
        offer_id = stock.offer.id

        nb_queries = 1  # select offer
        nb_queries += 1  # select stocks
        nb_queries += 1  # select mediations
        nb_queries += 1  # select activation_code
        nb_queries += 1  # select chronicles
        nb_queries += 1  # select futureOffer
        with assert_num_queries(nb_queries):
            with assert_no_duplicated_queries():
                response = client.get(f"/native/v1/offer/{offer_id}")
                assert response.status_code == 200

        assert response.json["stocks"][0]["activationCode"] is None

    @time_machine.travel("2020-01-01")
    def test_get_expired_offer(self, client):
        stock = offers_factories.EventStockFactory(beginningDatetime=datetime.utcnow() - timedelta(days=1))

        offer_id = stock.offer.id

        nb_queries = 1  # select offer
        nb_queries += 1  # select stocks
        nb_queries += 1  # select mediations
        nb_queries += 1  # select chronicles
        nb_queries += 1  # select futureOffer
        with assert_num_queries(nb_queries):
            with assert_no_duplicated_queries():
                response = client.get(f"/native/v1/offer/{offer_id}")

        assert response.json["isExpired"]

    def test_get_offer_not_found(self, client):
        # select offer
        # rollback
        with assert_num_queries(2):
            response = client.get("/native/v1/offer/1")

        assert response.status_code == 404

    @pytest.mark.parametrize(
        "validation", [OfferValidationStatus.DRAFT, OfferValidationStatus.PENDING, OfferValidationStatus.REJECTED]
    )
    def test_get_non_approved_offer(self, client, validation):
        offer = offers_factories.OfferFactory(validation=validation)

        offer_id = offer.id
        # select offer
        # rollback
        with assert_num_queries(2):
            response = client.get(f"/native/v1/offer/{offer_id}")
            assert response.status_code == 404

    @pytest.mark.features(ENABLE_CDS_IMPLEMENTATION=True)
    @patch("pcapi.core.offers.api.external_bookings_api.get_shows_stock")
    def test_get_cds_sync_offer_updates_stock(self, mocked_get_shows_stock, client):
        movie_id = 54
        show_id = 5008

        mocked_get_shows_stock.return_value = {5008: 0}
        cds_provider = get_provider_by_local_class("CDSStocks")
        venue_provider = providers_factories.VenueProviderFactory(provider=cds_provider)
        cinema_provider_pivot = providers_factories.CinemaProviderPivotFactory(
            venue=venue_provider.venue,
            provider=venue_provider.provider,
            idAtProvider=venue_provider.venueIdAtOfferProvider,
        )
        providers_factories.CDSCinemaDetailsFactory(cinemaProviderPivot=cinema_provider_pivot)

        offer_id_at_provider = f"{movie_id}%{venue_provider.venue.siret}"
        offer = offers_factories.OfferFactory(
            subcategoryId=subcategories.SEANCE_CINE.id,
            idAtProvider=offer_id_at_provider,
            lastProviderId=venue_provider.providerId,
            venue=venue_provider.venue,
        )
        stock = offers_factories.EventStockFactory(
            offer=offer,
            idAtProviders=f"{offer_id_at_provider}#{show_id}",
        )
        offer_id = offer.id

        nb_queries = 1  # select offer
        nb_queries += 1  # select stocks
        nb_queries += 1  # select mediations
        nb_queries += 1  # check cinema venue_provider exists
        nb_queries += 1  # select active cinema provider
        nb_queries += 1  # select cinema_provider_pivot
        nb_queries += 1  # select feature
        nb_queries += 1  # update stock
        nb_queries += 1  # select chronicles
        nb_queries += 1  # select futureOffer
        with assert_num_queries(nb_queries):
            response = client.get(f"/native/v1/offer/{offer_id}")
            assert response.status_code == 200

        assert stock.remainingQuantity == 0
        assert response.json["stocks"][0]["isSoldOut"]

    @time_machine.travel("2023-01-01")
    @pytest.mark.features(ENABLE_BOOST_API_INTEGRATION=True)
    @patch("pcapi.connectors.boost.requests.get")
    def test_get_boost_sync_offer_updates_stock(self, request_get, client):
        movie_id = 207
        first_show_id = 36683
        will_be_sold_out_show = 36684

        response_return_value = mock.MagicMock(status_code=200, text="", headers={"Content-Type": "application/json"})
        response_return_value.json = mock.MagicMock(
            return_value=boost_fixtures.ShowtimesWithFilmIdEndpointResponse.PAGE_1_JSON_DATA_3_SHOWTIMES
        )
        request_get.return_value = response_return_value

        boost_provider = get_provider_by_local_class("BoostStocks")
        venue_provider = providers_factories.VenueProviderFactory(provider=boost_provider)
        cinema_provider_pivot = providers_factories.CinemaProviderPivotFactory(
            venue=venue_provider.venue,
            provider=venue_provider.provider,
            idAtProvider=venue_provider.venueIdAtOfferProvider,
        )
        providers_factories.BoostCinemaDetailsFactory(
            cinemaProviderPivot=cinema_provider_pivot, cinemaUrl="https://cinema-0.example.com/"
        )
        offer_id_at_provider = f"{movie_id}%{venue_provider.venueId}%Boost"
        offer = offers_factories.OfferFactory(
            subcategoryId=subcategories.SEANCE_CINE.id,
            idAtProvider=offer_id_at_provider,
            lastProviderId=venue_provider.providerId,
            venue=venue_provider.venue,
        )
        first_show_stock = offers_factories.EventStockFactory(
            offer=offer, idAtProviders=f"{offer_id_at_provider}#{first_show_id}", quantity=96
        )
        will_be_sold_out_show_stock = offers_factories.EventStockFactory(
            offer=offer, idAtProviders=f"{offer_id_at_provider}#{will_be_sold_out_show}", quantity=96
        )

        offer_id = offer.id
        nb_queries = 1  # select offer
        nb_queries += 1  # select stocks
        nb_queries += 1  # select mediations
        nb_queries += 1  # select EXISTS venue_provider
        nb_queries += 1  # select EXISTS provider
        nb_queries += 1  # select cinema_provider_pivot
        nb_queries += 1  # select feature
        nb_queries += 1  # select EXISTS provider
        nb_queries += 1  # select boost_cinema_details
        nb_queries += 1  # update stock
        nb_queries += 1  # select chronicles
        nb_queries += 1  # select futureOffer
        with assert_num_queries(nb_queries):
            response = client.get(f"/native/v1/offer/{offer_id}")
            assert response.status_code == 200
        assert first_show_stock.remainingQuantity == 96
        assert will_be_sold_out_show_stock.remainingQuantity == 0

    @pytest.mark.features(ENABLE_CGR_INTEGRATION=True)
    def test_get_cgr_sync_offer_updates_stock(self, requests_mock, client):
        allocine_movie_id = 234099
        still_scheduled_show = 182021
        descheduled_show = 182022
        requests_mock.get(
            "https://cgr-cinema-0.example.com/web_service?wsdl", text=soap_definitions.WEB_SERVICE_DEFINITION
        )
        requests_mock.post(
            "https://cgr-cinema-0.example.com/web_service",
            text=cgr_fixtures.cgr_response_template([cgr_fixtures.FILM_234099_WITH_THREE_SEANCES]),
        )

        cgr_provider = get_provider_by_local_class("CGRStocks")
        venue_provider = providers_factories.VenueProviderFactory(provider=cgr_provider)
        cinema_provider_pivot = providers_factories.CinemaProviderPivotFactory(
            venue=venue_provider.venue,
            provider=venue_provider.provider,
            idAtProvider=venue_provider.venueIdAtOfferProvider,
        )
        providers_factories.CGRCinemaDetailsFactory(
            cinemaProviderPivot=cinema_provider_pivot, cinemaUrl="https://cgr-cinema-0.example.com/web_service"
        )
        offer_id_at_provider = f"{allocine_movie_id}%{venue_provider.venueId}%CGR"
        offer = offers_factories.OfferFactory(
            subcategoryId=subcategories.SEANCE_CINE.id,
            idAtProvider=offer_id_at_provider,
            lastProviderId=venue_provider.providerId,
            venue=venue_provider.venue,
        )
        still_scheduled_show_stock = offers_factories.EventStockFactory(
            offer=offer, idAtProviders=f"{offer_id_at_provider}#{still_scheduled_show}", quantity=95
        )
        descheduled_show_stock = offers_factories.EventStockFactory(
            offer=offer, idAtProviders=f"{offer_id_at_provider}#{descheduled_show}", quantity=95
        )

        offer_id = offer.id
        nb_queries = 1  # select offer
        nb_queries += 1  # select stocks
        nb_queries += 1  # select mediations
        nb_queries += 1  # select EXISTS venue_provider
        nb_queries += 1  # select EXISTS provider
        nb_queries += 1  # select cinema_provider_pivot
        nb_queries += 1  # select feature
        nb_queries += 1  # select EXISTS provider
        nb_queries += 1  # select cgr_cinema_details
        nb_queries += 1  # update stock
        nb_queries += 1  # select chronicles
        nb_queries += 1  # select futureOffer
        with assert_num_queries(nb_queries):
            response = client.get(f"/native/v1/offer/{offer_id}")
            assert response.status_code == 200

        assert still_scheduled_show_stock.remainingQuantity == 95
        assert descheduled_show_stock.remainingQuantity == 0

    @pytest.mark.features(ENABLE_CDS_IMPLEMENTATION=True)
    def test_get_inactive_cinema_provider_offer(self, client):
        cds_provider = get_provider_by_local_class("CDSStocks")
        venue_provider = providers_factories.VenueProviderFactory(provider=cds_provider, isActive=False)
        cinema_provider_pivot = providers_factories.CinemaProviderPivotFactory(
            venue=venue_provider.venue,
            provider=venue_provider.provider,
            idAtProvider=venue_provider.venueIdAtOfferProvider,
        )
        providers_factories.CDSCinemaDetailsFactory(cinemaProviderPivot=cinema_provider_pivot)
        offer = offers_factories.OfferFactory(
            subcategoryId=subcategories.SEANCE_CINE.id,
            idAtProvider="toto",
            lastProviderId=venue_provider.providerId,
            venue=venue_provider.venue,
        )
        offers_factories.EventStockFactory(offer=offer, idAtProviders="toto")

        offer_id = offer.id
        nb_query = 1  # select offer
        nb_query += 1  # select stocks
        nb_query += 1  # select mediations
        nb_query += 1  # check cinema venue_provider exists
        nb_query += 1  # select active cinema provider
        nb_query += 1  # update offer
        nb_query += 1  # select feature
        nb_query += 1  # select chronicles
        nb_query += 1  # select futureOffer
        with assert_num_queries(nb_query):
            response = client.get(f"/native/v1/offer/{offer_id}")
            assert response.status_code == 200

        assert response.json["isReleased"] is False
        assert offer.isActive is False

    def should_have_metadata_describing_the_offer(self, client):
        offer = offers_factories.ThingOfferFactory()

        offer_id = offer.id
        nb_query = 1  # select offer
        nb_query += 1  # select stocks
        nb_query += 1  # select mediations
        nb_query += 1  # select chronicles
        nb_query += 1  # select futureOffer
        with assert_num_queries(nb_query):
            response = client.get(f"/native/v1/offer/{offer_id}")
            assert response.status_code == 200

        assert isinstance(response.json["metadata"], dict)
        assert response.json["metadata"]["@type"] == "Product"

    def should_not_return_soft_deleted_offer(self, client):
        offer = offers_factories.OfferFactory()
        offers_factories.StockFactory(offer=offer, quantity=1, isSoftDeleted=True)
        non_deleted_stock = offers_factories.StockFactory(offer=offer, quantity=1)

        offer_id = offer.id
        nb_query = 1  # select offer
        nb_query += 1  # select stocks
        nb_query += 1  # select mediations
        nb_query += 1  # select chronicles
        nb_query += 1  # select futureOffer
        with assert_num_queries(nb_query):
            with assert_no_duplicated_queries():
                response = client.get(f"/native/v1/offer/{offer_id}")

        assert response.status_code == 200
        assert len(response.json["stocks"]) == 1
        assert response.json["stocks"][0]["id"] == non_deleted_stock.id

    def should_not_update_offer_stocks_when_getting_offer(self, client):
        offer = offers_factories.OfferFactory()
        offers_factories.StockFactory(offer=offer, quantity=1, isSoftDeleted=True)
        offers_factories.StockFactory(offer=offer, quantity=1)

        offer_id = offer.id
        nb_query = 1  # select offer
        nb_query += 1  # select stocks
        nb_query += 1  # select mediations
        nb_query += 1  # select chronicles
        nb_query += 1  # select futureOffer
        with assert_num_queries(nb_query):
            response = client.get(f"/native/v1/offer/{offer_id}")

        assert response.status_code == 200
        assert len(response.json["stocks"]) == 1
        assert len(offer.stocks) == 2

    def test_get_offer_with_product_mediation_and_thumb(self, client):
        product = offers_factories.ProductFactory(thumbCount=1, subcategoryId=subcategories.LIVRE_PAPIER.id)
        uuid = "1"
        product_mediation = offers_factories.ProductMediationFactory(
            product=product, uuid=uuid, imageType=TiteliveImageType.RECTO
        )
        offer = offers_factories.OfferFactory(
            product=product, venue__isPermanent=True, subcategoryId=subcategories.LIVRE_PAPIER.id
        )
        offers_factories.ThingStockFactory(offer=offer, price=12.34)

        offer_id = offer.id
        # 1. select offer
        # 2. select stocks
        # 3. select mediations
        # 4. select chronicles
        # 5. select futureOffer
        # 6. select artists
        with assert_num_queries(6):
            response = client.get(f"/native/v1/offer/{offer_id}")

        assert response.status_code == 200
        assert response.json["image"] == {
            "url": product_mediation.url,
            "credit": None,
        }

    def test_get_offer_with_two_product_mediation(self, client):
        product = offers_factories.ProductFactory(thumbCount=0, subcategoryId=subcategories.LIVRE_PAPIER.id)
        uuid = "recto"
        product_mediation = offers_factories.ProductMediationFactory(
            product=product, uuid=uuid, imageType=TiteliveImageType.RECTO
        )
        offers_factories.ProductMediationFactory(product=product, imageType=TiteliveImageType.VERSO)
        offer = offers_factories.OfferFactory(
            product=product, venue__isPermanent=True, subcategoryId=subcategories.LIVRE_PAPIER.id
        )
        offers_factories.ThingStockFactory(offer=offer, price=12.34)

        offer_id = offer.id
        # 1. select offer
        # 2. select stocks
        # 3. select mediations
        # 4. select chronicles
        # 5. select futureOffer
        # 6. select artists
        with assert_num_queries(6):
            response = client.get(f"/native/v1/offer/{offer_id}")

        assert response.status_code == 200
        assert response.json["image"] == {
            "url": product_mediation.url,
            "credit": None,
        }

    def test_get_offer_with_thumb_only(self, client):
        product = offers_factories.ProductFactory(id=111, thumbCount=1, subcategoryId=subcategories.LIVRE_PAPIER.id)
        offer = offers_factories.OfferFactory(
            product=product, venue__isPermanent=True, subcategoryId=subcategories.LIVRE_PAPIER.id
        )
        offers_factories.ThingStockFactory(offer=offer, price=12.34)

        offer_id = offer.id
        # 1. select offer
        # 2. select stocks
        # 3. select mediations
        # 4. select chronicles
        # 5. select futureOffer
        # 6. select artists
        with assert_num_queries(6):
            response = client.get(f"/native/v1/offer/{offer_id}")

        assert response.status_code == 200
        assert response.json["image"] == {
            "url": "http://localhost/storage/thumbs/products/N4",
            "credit": None,
        }

    def test_get_offer_with_mediation_and_product_mediation(self, client):
        product = offers_factories.ProductFactory(thumbCount=1, subcategoryId=subcategories.LIVRE_PAPIER.id)
        offers_factories.ProductMediationFactory(product=product, imageType=TiteliveImageType.RECTO)
        offer = offers_factories.OfferFactory(
            product=product, venue__isPermanent=True, subcategoryId=subcategories.LIVRE_PAPIER.id
        )
        offers_factories.ThingStockFactory(offer=offer, price=12.34)
        offers_factories.MediationFactory(id=111, offer=offer, thumbCount=2, credit="street credit")

        offer_id = offer.id
        # 1. select offer
        # 2. select stocks
        # 3. select mediations
        # 4. select chronicles
        # 5. select futureOffer
        # 6. select artists
        with assert_num_queries(6):
            response = client.get(f"/native/v1/offer/{offer_id}")

        assert response.status_code == 200
        assert response.json["image"] == {
            "url": "http://localhost/storage/thumbs/mediations/N4_1",
            "credit": "street credit",
        }


class OffersV2Test:
    base_num_queries = 1  # select offer with joins
    base_num_queries += 1  # select stocks (selectinload)
    base_num_queries += 1  # select mediations (selectinload)
    base_num_queries += 1  # select chronicles (selectinload)
    base_num_queries += 1  # select futureOffer (selectinload)

    num_queries_with_product = 1  # select artists (selectinload)

    num_queries_for_cinema = 1  # select EXISTS venue_provider
    num_queries_for_cinema += 1  # select EXISTS provider

    num_queries_for_stock_sync = 1  # update stock
    num_queries_for_stock_sync += 1  # select cinema_provider_pivot

    @time_machine.travel("2020-01-01", tick=False)
    def test_get_event_offer(self, client):
        extra_data = {
            "allocineId": 12345,
            "author": "mandibule",
            "ean": "3838",
            "musicSubType": "502",
            "musicType": "501",
            "performer": "interprète",
            "showSubType": "101",
            "showType": "100",
            "stageDirector": "metteur en scène",
            "speaker": "intervenant",
            "visa": "vasi",
            "genres": ["ACTION", "DRAMA"],
            "cast": ["cast1", "cast2"],
            "editeur": "editeur",
            "gtl_id": "01030000",
            "releaseDate": "2020-01-01",
            "certificate": "Interdit aux moins de 18 ans",
        }
        offer = offers_factories.OfferFactory(
            subcategoryId=subcategories.SEANCE_CINE.id,
            isDuo=True,
            description="desk cryption",
            name="l'offre du siècle",
            withdrawalDetails="modalité de retrait",
            extraData=extra_data,
            durationMinutes=33,
            visualDisabilityCompliant=True,
            externalTicketOfficeUrl="https://url.com",
            venue__name="il est venu le temps des names",
        )
        offers_factories.MediationFactory(id=111, offer=offer, thumbCount=1, credit="street credit")

        bookable_stock = offers_factories.EventStockFactory(
            offer=offer,
            price=12.34,
            quantity=2,
            priceCategory__priceCategoryLabel__label="bookable",
            features=[
                cinema_providers_constants.ShowtimeFeatures.VF.value,
                cinema_providers_constants.ShowtimeFeatures.THREE_D.value,
                cinema_providers_constants.ShowtimeFeatures.ICE.value,
            ],
        )
        another_bookable_stock = offers_factories.EventStockFactory(
            offer=offer,
            price=12.34,
            quantity=3,
            priceCategory=bookable_stock.priceCategory,
            features=[
                cinema_providers_constants.ShowtimeFeatures.VO.value,
                cinema_providers_constants.ShowtimeFeatures.THREE_D.value,
            ],
        )
        expired_stock = offers_factories.EventStockFactory(
            offer=offer,
            price=45.67,
            beginningDatetime=datetime.utcnow() - timedelta(days=1),
            priceCategory__priceCategoryLabel__label="expired",
            features=[
                cinema_providers_constants.ShowtimeFeatures.VF.value,
                cinema_providers_constants.ShowtimeFeatures.ICE.value,
            ],
        )
        exhausted_stock = offers_factories.EventStockFactory(
            offer=offer,
            price=89.00,
            quantity=1,
            priceCategory__priceCategoryLabel__label="exhausted",
            features=[cinema_providers_constants.ShowtimeFeatures.VO.value],
        )

        BookingFactory(stock=bookable_stock, user__deposit__expirationDate=datetime(year=2031, month=12, day=31))
        BookingFactory(stock=exhausted_stock, user__deposit__expirationDate=datetime(year=2031, month=12, day=31))

        offer_id = offer.id
        with assert_num_queries(self.base_num_queries):
            response = client.get(f"/native/v2/offer/{offer_id}")

        assert response.status_code == 200

        assert response.json["id"] == offer.id
        assert response.json["accessibility"] == {
            "audioDisability": False,
            "mentalDisability": False,
            "motorDisability": False,
            "visualDisability": True,
        }
        assert sorted(response.json["stocks"], key=lambda stock: stock["id"]) == sorted(
            [
                {
                    "id": bookable_stock.id,
                    "price": 1234,
                    "beginningDatetime": "2020-01-31T00:00:00Z",
                    "bookingLimitDatetime": "2020-01-30T23:00:00Z",
                    "cancellationLimitDatetime": "2020-01-03T00:00:00Z",
                    "features": ["VF", "3D", "ICE"],
                    "isBookable": True,
                    "isForbiddenToUnderage": False,
                    "isSoldOut": False,
                    "isExpired": False,
                    "activationCode": None,
                    "priceCategoryLabel": "bookable",
                    "remainingQuantity": 1,
                },
                {
                    "id": another_bookable_stock.id,
                    "price": 1234,
                    "beginningDatetime": "2020-01-31T00:00:00Z",
                    "bookingLimitDatetime": "2020-01-30T23:00:00Z",
                    "cancellationLimitDatetime": "2020-01-03T00:00:00Z",
                    "features": ["VO", "3D"],
                    "isBookable": True,
                    "isForbiddenToUnderage": False,
                    "isSoldOut": False,
                    "isExpired": False,
                    "activationCode": None,
                    "priceCategoryLabel": "bookable",
                    "remainingQuantity": 3,
                },
                {
                    "id": expired_stock.id,
                    "price": 4567,
                    "beginningDatetime": "2019-12-31T00:00:00Z",
                    "bookingLimitDatetime": "2019-12-30T23:00:00Z",
                    "cancellationLimitDatetime": "2020-01-01T00:00:00Z",
                    "features": ["VF", "ICE"],
                    "isBookable": False,
                    "isForbiddenToUnderage": False,
                    "isSoldOut": True,
                    "isExpired": True,
                    "activationCode": None,
                    "priceCategoryLabel": "expired",
                    "remainingQuantity": 1000,
                },
                {
                    "id": exhausted_stock.id,
                    "price": 8900,
                    "beginningDatetime": "2020-01-31T00:00:00Z",
                    "bookingLimitDatetime": "2020-01-30T23:00:00Z",
                    "cancellationLimitDatetime": "2020-01-03T00:00:00Z",
                    "features": ["VO"],
                    "isBookable": False,
                    "isForbiddenToUnderage": False,
                    "isSoldOut": True,
                    "isExpired": False,
                    "activationCode": None,
                    "priceCategoryLabel": "exhausted",
                    "remainingQuantity": 0,
                },
            ],
            key=lambda stock: stock["id"],
        )
        assert response.json["description"] == "desk cryption"
        assert response.json["externalTicketOfficeUrl"] == "https://url.com"
        assert response.json["expenseDomains"] == ["all"]
        assert response.json["extraData"] == {
            "allocineId": 12345,
            "author": "mandibule",
            "ean": "3838",
            "durationMinutes": 33,
            "musicSubType": "Acid Jazz",
            "musicType": "Jazz",
            "performer": "interprète",
            "showSubType": "Carnaval",
            "showType": "Arts de la rue",
            "speaker": "intervenant",
            "stageDirector": "metteur en scène",
            "visa": "vasi",
            "genres": ["Action", "Drame"],
            "cast": ["cast1", "cast2"],
            "editeur": "editeur",
            "gtlLabels": {
                "label": "Œuvres classiques",
                "level01Label": "Littérature",
                "level02Label": "Œuvres classiques",
                "level03Label": None,
                "level04Label": None,
            },
            "releaseDate": "2020-01-01",
            "certificate": "Interdit aux moins de 18 ans",
            "bookFormat": None,
        }
        assert response.json["images"] == {
            "recto": {
                "url": "http://localhost/storage/thumbs/mediations/N4",
                "credit": "street credit",
            }
        }
        assert response.json["isExpired"] is False
        assert response.json["isForbiddenToUnderage"] is False
        assert response.json["isSoldOut"] is False
        assert response.json["isDuo"] is True
        assert response.json["isEducational"] is False
        assert response.json["isDigital"] is False
        assert response.json["isReleased"] is True
        assert response.json["name"] == "l'offre du siècle"
        assert response.json["subcategoryId"] == subcategories.SEANCE_CINE.id
        assert response.json["venue"] == {
            "id": offer.venue.id,
            "address": "1 boulevard Poissonnière",
            "city": "Paris",
            "coordinates": {
                "latitude": 48.87004,
                "longitude": 2.3785,
            },
            "name": "il est venu le temps des names",
            "offerer": {"name": offer.venue.managingOfferer.name},
            "postalCode": "75002",
            "publicName": "il est venu le temps des names",
            "isPermanent": False,
            "isOpenToPublic": False,
            "timezone": "Europe/Paris",
            "bannerUrl": offer.venue.bannerUrl,
        }
        assert response.json["withdrawalDetails"] == "modalité de retrait"
        assert response.json["publicationDate"] is None

    def test_get_offer_with_unlimited_stock(self, client):
        product = offers_factories.ProductFactory(thumbCount=1, subcategoryId=subcategories.LIVRE_PAPIER.id)
        offer = offers_factories.OfferFactory(product=product, venue__isPermanent=True)
        offers_factories.ThingStockFactory(offer=offer, price=12.34, quantity=None)

        offer_id = offer.id
        with assert_num_queries(self.base_num_queries + self.num_queries_with_product):
            response = client.get(f"/native/v2/offer/{offer_id}")

        assert response.status_code == 200
        assert response.json["stocks"][0]["remainingQuantity"] is None

    def test_get_thing_offer(self, client):
        offer = offers_factories.OfferFactory(venue__isPermanent=True, subcategoryId=subcategories.CARTE_MUSEE.id)
        offers_factories.ThingStockFactory(offer=offer, price=12.34)

        offer_id = offer.id
        with assert_num_queries(self.base_num_queries):
            response = client.get(f"/native/v2/offer/{offer_id}")

        assert response.status_code == 200
        assert not response.json["stocks"][0]["beginningDatetime"]
        assert response.json["stocks"][0]["price"] == 1234
        assert response.json["stocks"][0]["priceCategoryLabel"] is None
        assert response.json["stocks"][0]["remainingQuantity"] == 1000
        assert response.json["subcategoryId"] == "CARTE_MUSEE"
        assert response.json["isEducational"] is False
        assert not response.json["isExpired"]
        assert response.json["venue"]["isPermanent"]
        assert response.json["venue"]["isOpenToPublic"]
        assert response.json["stocks"][0]["features"] == []

    @pytest.mark.parametrize(
        "provider_class,ff_name,ff_value,booking_disabled",
        [
            ("EMSStocks", "DISABLE_EMS_EXTERNAL_BOOKINGS", True, True),
            ("EMSStocks", "DISABLE_EMS_EXTERNAL_BOOKINGS", False, False),
            ("CGRStocks", "DISABLE_CGR_EXTERNAL_BOOKINGS", True, True),
            ("CGRStocks", "DISABLE_CGR_EXTERNAL_BOOKINGS", False, False),
            ("CDSStocks", "DISABLE_CDS_EXTERNAL_BOOKINGS", True, True),
            ("CDSStocks", "DISABLE_CDS_EXTERNAL_BOOKINGS", False, False),
            ("BoostStocks", "DISABLE_BOOST_EXTERNAL_BOOKINGS", True, True),
            ("BoostStocks", "DISABLE_BOOST_EXTERNAL_BOOKINGS", False, False),
            ("BoostStocks", "DISABLE_EMS_EXTERNAL_BOOKINGS", True, False),
        ],
    )
    def test_offer_external_booking_is_disabled_by_ff(
        self, features, client, provider_class, ff_name, ff_value, booking_disabled
    ):
        provider = get_provider_by_local_class(provider_class)
        product = offers_factories.ProductFactory(thumbCount=1, subcategoryId=subcategories.SEANCE_CINE.id)
        offer = offers_factories.OfferFactory(
            product=product,
            venue__isPermanent=True,
            subcategoryId=subcategories.SEANCE_CINE.id,
            lastProvider=provider,
        )
        providers_factories.VenueProviderFactory(venue=offer.venue, provider=provider)

        offer_id = offer.id
        setattr(features, ff_name, ff_value)
        num_queries = self.base_num_queries + self.num_queries_for_cinema + self.num_queries_for_stock_sync
        num_queries += 1  # update offer
        num_queries += 1  # select feature
        with assert_num_queries(num_queries):
            response = client.get(f"/native/v2/offer/{offer_id}")

        assert response.status_code == 200
        assert response.json["isExternalBookingsDisabled"] is booking_disabled

    def test_get_digital_offer_with_available_activation_and_no_expiration_date(self, client):
        # given
        stock = offers_factories.StockWithActivationCodesFactory()
        offer_id = stock.offer.id

        # when
        num_queries = self.base_num_queries
        num_queries += 1  # select activation_code
        with assert_num_queries(num_queries):
            response = client.get(f"/native/v2/offer/{offer_id}")

        # then
        assert response.status_code == 200
        assert response.json["stocks"][0]["activationCode"] == {"expirationDate": None}

    def test_get_digital_offer_with_available_activation_code_and_expiration_date(self, client):
        # given
        stock = offers_factories.StockWithActivationCodesFactory(activationCodes__expirationDate=datetime(2050, 1, 1))
        offer_id = stock.offer.id

        # when
        num_queries = self.base_num_queries
        num_queries += 1  # select activation_code
        with assert_num_queries(num_queries):
            response = client.get(f"/native/v2/offer/{offer_id}")

        # then
        assert response.status_code == 200
        assert response.json["stocks"][0]["activationCode"] == {"expirationDate": "2050-01-01T00:00:00Z"}

    def test_get_digital_offer_without_available_activation_code(self, client):
        # given
        stock = offers_factories.StockWithActivationCodesFactory(activationCodes__expirationDate=datetime(2000, 1, 1))
        offer_id = stock.offer.id

        # when
        nb_query = self.base_num_queries
        nb_query += 1  # select activation_code
        with assert_num_queries(nb_query):
            response = client.get(f"/native/v2/offer/{offer_id}")

        # then
        assert response.status_code == 200
        assert response.json["stocks"][0]["activationCode"] is None

    @time_machine.travel("2020-01-01")
    def test_get_expired_offer(self, client):
        stock = offers_factories.EventStockFactory(beginningDatetime=datetime.utcnow() - timedelta(days=1))

        offer_id = stock.offer.id
        with assert_num_queries(self.base_num_queries):
            response = client.get(f"/native/v2/offer/{offer_id}")

        assert response.json["isExpired"]

    def test_get_offer_not_found(self, client):
        # 1. select offer
        # 2. rollback
        with assert_num_queries(2):
            response = client.get("/native/v2/offer/1")

        assert response.status_code == 404

    @pytest.mark.parametrize(
        "validation", [OfferValidationStatus.DRAFT, OfferValidationStatus.PENDING, OfferValidationStatus.REJECTED]
    )
    def test_get_non_approved_offer(self, client, validation):
        offer = offers_factories.OfferFactory(validation=validation)

        offer_id = offer.id
        # 1. select offer
        # 2. rollback
        with assert_num_queries(2):
            response = client.get(f"/native/v2/offer/{offer_id}")
            assert response.status_code == 404

    @pytest.mark.features(ENABLE_CDS_IMPLEMENTATION=True)
    @patch("pcapi.core.offers.api.external_bookings_api.get_shows_stock")
    def test_get_cds_sync_offer_updates_stock(self, mocked_get_shows_stock, client):
        movie_id = 54
        show_id = 5008

        mocked_get_shows_stock.return_value = {5008: 0}
        cds_provider = get_provider_by_local_class("CDSStocks")
        venue_provider = providers_factories.VenueProviderFactory(provider=cds_provider)
        cinema_provider_pivot = providers_factories.CinemaProviderPivotFactory(
            venue=venue_provider.venue,
            provider=venue_provider.provider,
            idAtProvider=venue_provider.venueIdAtOfferProvider,
        )
        providers_factories.CDSCinemaDetailsFactory(cinemaProviderPivot=cinema_provider_pivot)

        offer_id_at_provider = f"{movie_id}%{venue_provider.venue.siret}"
        offer = offers_factories.OfferFactory(
            subcategoryId=subcategories.SEANCE_CINE.id,
            idAtProvider=offer_id_at_provider,
            lastProviderId=venue_provider.providerId,
            venue=venue_provider.venue,
        )
        stock = offers_factories.EventStockFactory(
            offer=offer,
            idAtProviders=f"{offer_id_at_provider}#{show_id}",
        )

        offer_id = offer.id
        num_queries = self.base_num_queries + self.num_queries_for_cinema + self.num_queries_for_stock_sync
        num_queries += 1  # select feature
        with assert_num_queries(num_queries):
            response = client.get(f"/native/v2/offer/{offer_id}")

        assert stock.remainingQuantity == 0
        assert response.json["stocks"][0]["isSoldOut"]

    @time_machine.travel("2023-01-01")
    @pytest.mark.features(ENABLE_BOOST_API_INTEGRATION=True)
    @patch("pcapi.connectors.boost.requests.get")
    def test_get_boost_sync_offer_updates_stock(self, request_get, client):
        movie_id = 207
        first_show_id = 36683
        will_be_sold_out_show = 36684

        response_return_value = mock.MagicMock(status_code=200, text="", headers={"Content-Type": "application/json"})
        response_return_value.json = mock.MagicMock(
            return_value=boost_fixtures.ShowtimesWithFilmIdEndpointResponse.PAGE_1_JSON_DATA_3_SHOWTIMES
        )
        request_get.return_value = response_return_value

        boost_provider = get_provider_by_local_class("BoostStocks")
        venue_provider = providers_factories.VenueProviderFactory(provider=boost_provider)
        cinema_provider_pivot = providers_factories.CinemaProviderPivotFactory(
            venue=venue_provider.venue,
            provider=venue_provider.provider,
            idAtProvider=venue_provider.venueIdAtOfferProvider,
        )
        providers_factories.BoostCinemaDetailsFactory(
            cinemaProviderPivot=cinema_provider_pivot, cinemaUrl="https://cinema-0.example.com/"
        )
        offer_id_at_provider = f"{movie_id}%{venue_provider.venueId}%Boost"
        offer = offers_factories.OfferFactory(
            subcategoryId=subcategories.SEANCE_CINE.id,
            idAtProvider=offer_id_at_provider,
            lastProviderId=venue_provider.providerId,
            venue=venue_provider.venue,
        )
        first_show_stock = offers_factories.EventStockFactory(
            offer=offer, idAtProviders=f"{offer_id_at_provider}#{first_show_id}", quantity=96
        )
        will_be_sold_out_show_stock = offers_factories.EventStockFactory(
            offer=offer, idAtProviders=f"{offer_id_at_provider}#{will_be_sold_out_show}", quantity=96
        )

        offer_id = offer.id
        num_queries = self.base_num_queries + self.num_queries_for_cinema + self.num_queries_for_stock_sync
        num_queries += 1  # select feature
        num_queries += 1  # select EXISTS venue_provider
        num_queries += 1  # select boost_cinema_details
        with assert_num_queries(num_queries):
            response = client.get(f"/native/v2/offer/{offer_id}")
        assert response.status_code == 200
        assert first_show_stock.remainingQuantity == 96
        assert will_be_sold_out_show_stock.remainingQuantity == 0

    @pytest.mark.features(ENABLE_CGR_INTEGRATION=True)
    def test_get_cgr_sync_offer_updates_stock(self, requests_mock, client):
        allocine_movie_id = 234099
        still_scheduled_show = 182021
        descheduled_show = 182022
        requests_mock.get(
            "https://cgr-cinema-0.example.com/web_service?wsdl", text=soap_definitions.WEB_SERVICE_DEFINITION
        )
        requests_mock.post(
            "https://cgr-cinema-0.example.com/web_service",
            text=cgr_fixtures.cgr_response_template([cgr_fixtures.FILM_234099_WITH_THREE_SEANCES]),
        )

        cgr_provider = get_provider_by_local_class("CGRStocks")
        venue_provider = providers_factories.VenueProviderFactory(provider=cgr_provider)
        cinema_provider_pivot = providers_factories.CinemaProviderPivotFactory(
            venue=venue_provider.venue,
            provider=venue_provider.provider,
            idAtProvider=venue_provider.venueIdAtOfferProvider,
        )
        providers_factories.CGRCinemaDetailsFactory(
            cinemaProviderPivot=cinema_provider_pivot, cinemaUrl="https://cgr-cinema-0.example.com/web_service"
        )
        offer_id_at_provider = f"{allocine_movie_id}%{venue_provider.venueId}%CGR"
        offer = offers_factories.OfferFactory(
            subcategoryId=subcategories.SEANCE_CINE.id,
            idAtProvider=offer_id_at_provider,
            lastProviderId=venue_provider.providerId,
            venue=venue_provider.venue,
        )
        still_scheduled_show_stock = offers_factories.EventStockFactory(
            offer=offer, idAtProviders=f"{offer_id_at_provider}#{still_scheduled_show}", quantity=95
        )
        descheduled_show_stock = offers_factories.EventStockFactory(
            offer=offer, idAtProviders=f"{offer_id_at_provider}#{descheduled_show}", quantity=95
        )

        offer_id = offer.id
        num_queries = self.base_num_queries + self.num_queries_for_cinema + self.num_queries_for_stock_sync
        num_queries += 1  # select feature
        num_queries += 1  # select EXISTS venue_provider
        num_queries += 1  # select cgr_cinema_details
        with assert_num_queries(num_queries):
            response = client.get(f"/native/v2/offer/{offer_id}")

        assert response.status_code == 200
        assert still_scheduled_show_stock.remainingQuantity == 95
        assert descheduled_show_stock.remainingQuantity == 0

    @pytest.mark.features(ENABLE_EMS_INTEGRATION=True)
    @patch("pcapi.connectors.ems.requests.post")
    def test_offer_route_does_not_crash_when_ems_errors(self, requests_post, client):
        requests_post.return_value = mock.MagicMock(status_code=500)

        provider = get_provider_by_local_class("EMSStocks")
        venue = VenueFactory(isPermanent=True)
        venue_provider = providers_factories.VenueProviderFactory(provider=provider, venue=venue)
        cinema_provider_pivot = providers_factories.CinemaProviderPivotFactory(
            venue=venue,
            provider=provider,
            idAtProvider=venue_provider.venueIdAtOfferProvider,
        )
        providers_factories.EMSCinemaProviderPivotFactory(cinemaProviderPivot=cinema_provider_pivot, venue=venue)

        allocine_movie_id = 234099
        offer_id_at_provider = f"{allocine_movie_id}%{venue.id}%EMS"
        product = offers_factories.ProductFactory(subcategoryId=subcategories.SEANCE_CINE.id)
        offer = offers_factories.OfferFactory(
            product=product,
            venue=venue,
            lastProvider=provider,
            idAtProvider=offer_id_at_provider,
            subcategoryId=subcategories.SEANCE_CINE.id,
        )
        offers_factories.EventStockFactory(offer=offer, quantity=1)

        offer_id = offer.id
        num_queries = self.base_num_queries + self.num_queries_with_product + self.num_queries_for_cinema
        num_queries += 1  # select cinema_provider_pivot
        num_queries += 1  # select feature
        num_queries += 1  # select EXISTS venue_provider
        with assert_num_queries(num_queries):
            response = client.get(f"/native/v2/offer/{offer_id}")

        assert response.status_code == 200
        assert offer.stocks[0].remainingQuantity == 1

    @pytest.mark.features(ENABLE_CGR_INTEGRATION=True)
    def test_offer_route_does_not_crash_when_cgr_errors(self, requests_mock, client):
        requests_mock.get("https://cgr-cinema-0.example.com/?wsdl", text=soap_definitions.WEB_SERVICE_DEFINITION)
        requests_mock.post("https://cgr-cinema-0.example.com/", text="", status_code=500)

        provider = get_provider_by_local_class("CGRStocks")
        venue = VenueFactory(isPermanent=True)
        venue_provider = providers_factories.VenueProviderFactory(provider=provider, venue=venue)
        cinema_provider_pivot = providers_factories.CinemaProviderPivotFactory(
            venue=venue,
            provider=provider,
            idAtProvider=venue_provider.venueIdAtOfferProvider,
        )
        providers_factories.CGRCinemaDetailsFactory(cinemaProviderPivot=cinema_provider_pivot)

        allocine_movie_id = 234099
        offer_id_at_provider = f"{allocine_movie_id}%{venue.id}%CGR"
        offer = offers_factories.OfferFactory(
            venue=venue,
            lastProvider=provider,
            idAtProvider=offer_id_at_provider,
            subcategoryId=subcategories.SEANCE_CINE.id,
        )
        offers_factories.EventStockFactory(offer=offer, quantity=1)

        offer_id = offer.id
        num_queries = self.base_num_queries + self.num_queries_for_cinema
        num_queries += 1  # select cinema_provider_pivot
        num_queries += 1  # select EXISTS venue_provider
        num_queries += 1  # select feature
        num_queries += 1  # select cgr_cinema_details
        with assert_num_queries(num_queries):
            response = client.get(f"/native/v2/offer/{offer_id}")

        assert response.status_code == 200
        assert offer.stocks[0].remainingQuantity == 1

    @pytest.mark.features(ENABLE_CDS_IMPLEMENTATION=True)
    @patch("pcapi.connectors.cine_digital_service.requests.get")
    def test_offer_route_does_not_crash_when_cds_errors(self, requests_get, client):
        requests_get.return_value = mock.MagicMock(status_code=500)

        cds_provider = get_provider_by_local_class("CDSStocks")
        venue_provider = providers_factories.VenueProviderFactory(provider=cds_provider, isActive=False)
        cinema_provider_pivot = providers_factories.CinemaProviderPivotFactory(
            venue=venue_provider.venue,
            provider=venue_provider.provider,
            idAtProvider=venue_provider.venueIdAtOfferProvider,
        )
        providers_factories.CDSCinemaDetailsFactory(cinemaProviderPivot=cinema_provider_pivot)
        offer = offers_factories.OfferFactory(
            subcategoryId=subcategories.SEANCE_CINE.id,
            idAtProvider="toto",
            lastProviderId=venue_provider.providerId,
            venue=venue_provider.venue,
        )
        offers_factories.EventStockFactory(offer=offer, idAtProviders="toto", quantity=1)

        offer_id = offer.id
        num_queries = self.base_num_queries + self.num_queries_for_cinema
        num_queries += 1  # update offer (why?)
        num_queries += 1  # select feature
        with assert_num_queries(num_queries):
            response = client.get(f"/native/v2/offer/{offer_id}")

        assert response.status_code == 200
        assert offer.stocks[0].remainingQuantity == 1

    @pytest.mark.features(ENABLE_BOOST_API_INTEGRATION=True)
    @patch("pcapi.connectors.boost.requests.get")
    def test_offer_route_does_not_crash_when_boost_errors(self, requests_get, client):
        requests_get.return_value = mock.MagicMock(status_code=500)

        movie_id = 207
        first_show_id = 36683

        boost_provider = get_provider_by_local_class("BoostStocks")
        venue_provider = providers_factories.VenueProviderFactory(provider=boost_provider)
        cinema_provider_pivot = providers_factories.CinemaProviderPivotFactory(
            venue=venue_provider.venue,
            provider=venue_provider.provider,
            idAtProvider=venue_provider.venueIdAtOfferProvider,
        )
        providers_factories.BoostCinemaDetailsFactory(
            cinemaProviderPivot=cinema_provider_pivot, cinemaUrl="https://cinema-0.example.com/"
        )
        offer_id_at_provider = f"{movie_id}%{venue_provider.venueId}%Boost"
        offer = offers_factories.OfferFactory(
            subcategoryId=subcategories.SEANCE_CINE.id,
            idAtProvider=offer_id_at_provider,
            lastProviderId=venue_provider.providerId,
            venue=venue_provider.venue,
        )
        offers_factories.EventStockFactory(
            offer=offer, idAtProviders=f"{offer_id_at_provider}#{first_show_id}", quantity=1
        )

        offer_id = offer.id
        num_queries = self.base_num_queries + self.num_queries_for_cinema
        num_queries += 1  # select cinema_provider_pivot
        num_queries += 1  # select feature
        num_queries += 1  # select EXISTS venue_provider
        num_queries += 1  # select boost_cinema_details
        with assert_num_queries(num_queries):
            response = client.get(f"/native/v2/offer/{offer_id}")

        assert response.status_code == 200
        assert offer.stocks[0].remainingQuantity == 1

    @pytest.mark.features(ENABLE_CDS_IMPLEMENTATION=True)
    def test_get_inactive_cinema_provider_offer(self, client):
        cds_provider = get_provider_by_local_class("CDSStocks")
        venue_provider = providers_factories.VenueProviderFactory(provider=cds_provider, isActive=False)
        cinema_provider_pivot = providers_factories.CinemaProviderPivotFactory(
            venue=venue_provider.venue,
            provider=venue_provider.provider,
            idAtProvider=venue_provider.venueIdAtOfferProvider,
        )
        providers_factories.CDSCinemaDetailsFactory(cinemaProviderPivot=cinema_provider_pivot)
        offer = offers_factories.OfferFactory(
            subcategoryId=subcategories.SEANCE_CINE.id,
            idAtProvider="toto",
            lastProviderId=venue_provider.providerId,
            venue=venue_provider.venue,
        )
        offers_factories.EventStockFactory(offer=offer, idAtProviders="toto")

        offer_id = offer.id
        num_queries = self.base_num_queries + self.num_queries_for_cinema
        num_queries += 1  # update offer
        num_queries += 1  # select feature
        with assert_num_queries(num_queries):
            response = client.get(f"/native/v2/offer/{offer_id}")

        assert response.json["isReleased"] is False
        assert offer.isActive is False

    def test_get_closed_offerer_offer(self, client):
        offer = offers_factories.EventOfferFactory(venue__managingOfferer=offerers_factories.ClosedOffererFactory())
        offers_factories.EventStockFactory(offer=offer)

        offer_id = offer.id
        with assert_num_queries(self.base_num_queries):
            response = client.get(f"/native/v2/offer/{offer_id}")
            assert response.status_code == 200

        assert response.json["isReleased"] is False

    def should_have_metadata_describing_the_offer(self, client):
        offer = offers_factories.ThingOfferFactory()

        offer_id = offer.id
        with assert_num_queries(self.base_num_queries):
            response = client.get(f"/native/v2/offer/{offer_id}")

        assert isinstance(response.json["metadata"], dict)
        assert response.json["metadata"]["@type"] == "Product"

    def should_not_return_soft_deleted_offer(self, client):
        offer = offers_factories.OfferFactory()
        offers_factories.StockFactory(offer=offer, quantity=1, isSoftDeleted=True)
        non_deleted_stock = offers_factories.StockFactory(offer=offer, quantity=1)

        offer_id = offer.id
        with assert_num_queries(self.base_num_queries):
            response = client.get(f"/native/v2/offer/{offer_id}")

        assert response.status_code == 200
        assert len(response.json["stocks"]) == 1
        assert response.json["stocks"][0]["id"] == non_deleted_stock.id

    def should_not_update_offer_stocks_when_getting_offer(self, client):
        offer = offers_factories.OfferFactory()
        offers_factories.StockFactory(offer=offer, quantity=1, isSoftDeleted=True)
        offers_factories.StockFactory(offer=offer, quantity=1)

        offer_id = offer.id
        with assert_num_queries(self.base_num_queries):
            response = client.get(f"/native/v2/offer/{offer_id}")

        assert response.status_code == 200
        assert len(response.json["stocks"]) == 1
        assert len(offer.stocks) == 2

    def test_get_offer_with_product_mediation_and_thumb(self, client):
        product = offers_factories.ProductFactory(thumbCount=1, subcategoryId=subcategories.LIVRE_PAPIER.id)
        uuid = "11111111"
        offers_factories.ProductMediationFactory(product=product, uuid=uuid, imageType=TiteliveImageType.RECTO)
        offer = offers_factories.OfferFactory(
            product=product, venue__isPermanent=True, subcategoryId=subcategories.LIVRE_PAPIER.id
        )
        offers_factories.ThingStockFactory(offer=offer, price=12.34)

        offer_id = offer.id
        with assert_num_queries(self.base_num_queries + self.num_queries_with_product):
            response = client.get(f"/native/v2/offer/{offer_id}")

        assert response.status_code == 200
        assert response.json["images"] == {
            "recto": {
                "url": f"{settings.OBJECT_STORAGE_URL}/{settings.THUMBS_FOLDER_NAME}/{uuid}",
                "credit": None,
            }
        }

    def test_get_offer_with_two_product_mediation(self, client):
        product = offers_factories.ProductFactory(thumbCount=0, subcategoryId=subcategories.LIVRE_PAPIER.id)
        first_uuid = "11111111"
        second_uuid = "22222222"
        offers_factories.ProductMediationFactory(product=product, uuid=first_uuid, imageType=TiteliveImageType.RECTO)
        offers_factories.ProductMediationFactory(product=product, uuid=second_uuid, imageType=TiteliveImageType.VERSO)
        offer = offers_factories.OfferFactory(
            product=product, venue__isPermanent=True, subcategoryId=subcategories.LIVRE_PAPIER.id
        )
        offers_factories.ThingStockFactory(offer=offer, price=12.34)

        offer_id = offer.id
        with assert_num_queries(self.base_num_queries + self.num_queries_with_product):
            response = client.get(f"/native/v2/offer/{offer_id}")

        assert response.status_code == 200
        assert response.json["images"] == {
            "recto": {
                "url": f"{settings.OBJECT_STORAGE_URL}/{settings.THUMBS_FOLDER_NAME}/{first_uuid}",
                "credit": None,
            },
            "verso": {
                "url": f"{settings.OBJECT_STORAGE_URL}/{settings.THUMBS_FOLDER_NAME}/{second_uuid}",
                "credit": None,
            },
        }

    def test_get_offer_with_thumb_only(self, client):
        product = offers_factories.ProductFactory(id=111, thumbCount=1, subcategoryId=subcategories.LIVRE_PAPIER.id)
        offer = offers_factories.OfferFactory(
            product=product, venue__isPermanent=True, subcategoryId=subcategories.LIVRE_PAPIER.id
        )
        offers_factories.ThingStockFactory(offer=offer, price=12.34)

        offer_id = offer.id
        with assert_num_queries(self.base_num_queries + self.num_queries_with_product):
            response = client.get(f"/native/v2/offer/{offer_id}")

        assert response.status_code == 200
        assert response.json["images"] == {
            "recto": {
                "url": "http://localhost/storage/thumbs/products/N4",
                "credit": None,
            }
        }

    def test_get_offer_with_mediation_and_product_mediation(self, client):
        product = offers_factories.ProductFactory(thumbCount=1, subcategoryId=subcategories.LIVRE_PAPIER.id)
        offers_factories.ProductMediationFactory(product=product, imageType=TiteliveImageType.RECTO)
        offer = offers_factories.OfferFactory(
            product=product, venue__isPermanent=True, subcategoryId=subcategories.LIVRE_PAPIER.id
        )
        offers_factories.ThingStockFactory(offer=offer, price=12.34)
        offers_factories.MediationFactory(id=111, offer=offer, thumbCount=2, credit="street credit")

        offer_id = offer.id
        with assert_num_queries(self.base_num_queries + self.num_queries_with_product):
            response = client.get(f"/native/v2/offer/{offer_id}")

        assert response.status_code == 200
        assert response.json["images"] == {
            "recto": {
                "url": "http://localhost/storage/thumbs/mediations/N4_1",
                "credit": "street credit",
            }
        }

    def test_get_event_offer_with_reactions(self, client):
        offer = offers_factories.EventOfferFactory(subcategoryId=subcategories.SEANCE_CINE.id)
        offers_factories.EventStockFactory(offer=offer, price=12.34)
        ReactionFactory(offer=offer, reactionType=ReactionTypeEnum.LIKE)
        ReactionFactory(offer=offer, reactionType=ReactionTypeEnum.LIKE)
        ReactionFactory(offer=offer, reactionType=ReactionTypeEnum.DISLIKE)

        offer_id = offer.id
        with assert_num_queries(self.base_num_queries):
            response = client.get(f"/native/v2/offer/{offer_id}")

        assert response.status_code == 200
        assert response.json["reactionsCount"] == {"likes": 2}

    def test_get_offer_attached_to_product_with_user_reaction(self, client):
        product = offers_factories.ProductFactory(subcategoryId=subcategories.SEANCE_CINE.id)
        offer = offers_factories.EventOfferFactory(product=product)
        offers_factories.EventStockFactory(offer=offer, price=12.34)
        ReactionFactory(product=product, reactionType=ReactionTypeEnum.LIKE)
        ReactionFactory(product=product, reactionType=ReactionTypeEnum.LIKE)
        ReactionFactory(product=product, reactionType=ReactionTypeEnum.DISLIKE)

        offer_id = offer.id
        with assert_num_queries(self.base_num_queries + self.num_queries_with_product):
            response = client.get(f"/native/v2/offer/{offer_id}")

        assert response.status_code == 200
        assert response.json["reactionsCount"] == {"likes": 2}

    def test_get_event_offer_with_no_reactions(self, client):
        offer = offers_factories.EventOfferFactory(subcategoryId=subcategories.SEANCE_CINE.id)
        offers_factories.EventStockFactory(offer=offer, price=12.34)

        offer_id = offer.id
        with assert_num_queries(self.base_num_queries):
            response = client.get(f"/native/v2/offer/{offer_id}")

        assert response.status_code == 200
        assert response.json["reactionsCount"] == {"likes": 0}

    def test_offers_has_own_address(self, client):
        address = AddressFactory()
        oa = OffererAddressFactory(address=address)
        offer = offers_factories.OfferFactory(offererAddress=oa)

        offer_id = offer.id
        with assert_num_queries(self.base_num_queries):
            response = client.get(f"/native/v2/offer/{offer_id}/")
        response_offer = response.json

        assert response.status_code == 200
        assert response_offer["address"] == {
            "label": oa.label,
            "street": address.street,
            "postalCode": address.postalCode,
            "city": address.city,
            "coordinates": {"latitude": 48.87055, "longitude": 2.34765},
            "timezone": address.timezone,
        }

    def test_offer_with_no_extra_data(self, client):
        extra_data = {}
        offer = offers_factories.OfferFactory(
            extraData=extra_data,
        )

        offer_id = offer.id
        with assert_num_queries(self.base_num_queries):
            response = client.get(f"/native/v2/offer/{offer_id}")
        assert response.status_code == 200
        assert response.json["extraData"] == {
            "allocineId": None,
            "author": None,
            "ean": None,
            "durationMinutes": None,
            "musicSubType": None,
            "musicType": None,
            "performer": None,
            "showSubType": None,
            "showType": None,
            "speaker": None,
            "stageDirector": None,
            "visa": None,
            "genres": None,
            "cast": None,
            "editeur": None,
            "gtlLabels": None,
            "releaseDate": None,
            "certificate": None,
            "bookFormat": None,
        }

    def test_offer_extra_data_book_format_from_product(self, client):
        extra_data = {"bookFormat": BookFormat.POCHE}
        product = offers_factories.ProductFactory(
            thumbCount=1,
            subcategoryId=subcategories.LIVRE_PAPIER.id,
            extraData=extra_data,
        )
        offer = offers_factories.OfferFactory(
            product=product,
            venue__isPermanent=True,
            subcategoryId=subcategories.LIVRE_PAPIER.id,
        )

        offer_id = offer.id
        with assert_num_queries(self.base_num_queries + self.num_queries_with_product):
            response = client.get(f"/native/v2/offer/{offer_id}")
        assert response.status_code == 200
        assert response.json["extraData"]["bookFormat"] == "POCHE"

    def test_offer_extra_data_book_format(self, client):
        extra_data = {"bookFormat": BookFormat.MOYEN_FORMAT}
        offer = offers_factories.OfferFactory(extraData=extra_data)

        offer_id = offer.id
        with assert_num_queries(self.base_num_queries):
            response = client.get(f"/native/v2/offer/{offer_id}")
        assert response.status_code == 200
        assert response.json["extraData"]["bookFormat"] == "MOYEN FORMAT"

    def test_offer_with_chronicles(self, client):
        product = offers_factories.ProductFactory()
        offer = offers_factories.OfferFactory(product=product)
        chronicle = chronicles_factories.ChronicleFactory(
            products=[product],
            content="a " * 150,
            isActive=True,
            isSocialMediaDiffusible=True,
            isIdentityDiffusible=True,
        )

        # The following should not be displayed in the response
        chronicles_factories.ChronicleFactory(
            products=[product], isActive=False, isSocialMediaDiffusible=True
        )  # Not yet published by pass culture (isActive)
        chronicles_factories.ChronicleFactory(
            products=[product], isActive=True, isSocialMediaDiffusible=False
        )  # Not marked OK for publication by the author (isSocialMediaDiffusible)

        offer_id = offer.id
        with assert_num_queries(self.base_num_queries + self.num_queries_with_product):
            response = client.get(f"/native/v2/offer/{offer_id}")

        assert response.status_code == 200
        assert response.json["chronicles"] == [
            {
                "id": chronicle.id,
                "contentPreview": "a " * 126 + "a…",
                "dateCreated": date_utils.format_into_utc_date(chronicle.dateCreated),
                "author": {"firstName": chronicle.firstName, "age": chronicle.age, "city": chronicle.city},
            }
        ]

    def test_offer_with_n_chronicles(self, client):
        product = offers_factories.ProductFactory()
        offer = offers_factories.OfferFactory(product=product)
        chronicles_factories.ChronicleFactory.create_batch(
            MAX_PREVIEW_CHRONICLES + 5, products=[product], isActive=True, isSocialMediaDiffusible=True
        )

        offer_id = offer.id
        with assert_num_queries(self.base_num_queries + self.num_queries_with_product):
            response = client.get(f"/native/v2/offer/{offer_id}")

        assert response.status_code == 200
        assert len(response.json["chronicles"]) == MAX_PREVIEW_CHRONICLES

    def test_anonymize_author_of_chronicles(self, client):
        product = offers_factories.ProductFactory()
        offer = offers_factories.OfferFactory(product=product)
        chronicle = chronicles_factories.ChronicleFactory(
            products=[product],
            isActive=True,
            isSocialMediaDiffusible=True,
            firstName="Angharad",
            age=42,
            city="Dijon",
            isIdentityDiffusible=False,
        )

        offer_id = offer.id
        with assert_num_queries(self.base_num_queries + self.num_queries_with_product):
            response = client.get(f"/native/v2/offer/{offer_id}")
            assert response.status_code == 200
            assert len(response.json["chronicles"]) == 1

        chronicle = response.json["chronicles"][0]
        assert chronicle["author"] is None

    def test_future_offer(self, client):
        offer = offers_factories.OfferFactory()
        publication_date = datetime(2050, 1, 1)
        _ = offers_factories.FutureOfferFactory(offer=offer, publicationDate=publication_date)

        offer_id = offer.id
        with assert_num_queries(self.base_num_queries):
            response = client.get(f"/native/v2/offer/{offer_id}")

        assert response.status_code == 200
        assert response.json["publicationDate"] == "2050-01-01T00:00:00Z"

    def test_get_offer_with_artists(self, client):
        product = offers_factories.ProductFactory()
        offer = offers_factories.OfferFactory(product=product)
        artist_1 = artists_factories.ArtistFactory()
        artist_2 = artists_factories.ArtistFactory()
        artists_factories.ArtistProductLinkFactory(
            artist_id=artist_1.id, product_id=product.id, artist_type=ArtistType.AUTHOR
        )
        artists_factories.ArtistProductLinkFactory(
            artist_id=artist_2.id, product_id=product.id, artist_type=ArtistType.AUTHOR
        )

        offer_id = offer.id
        with assert_num_queries(self.base_num_queries + self.num_queries_with_product):
            response = client.get(f"/native/v2/offer/{offer_id}")

        assert response.status_code == 200
        assert sorted(response.json["artists"], key=lambda a: a["id"]) == sorted(
            [
                {"id": artist_1.id, "name": artist_1.name, "image": artist_1.image},
                {"id": artist_2.id, "name": artist_2.name, "image": artist_2.image},
            ],
            key=lambda a: a["id"],
        )


class OffersStocksTest:
    def test_return_empty_on_empty_request(self, client):
        response = client.post("/native/v1/offers/stocks", json={"offer_ids": []})

        assert response.status_code == 200
        assert response.json == {"offers": []}

    def test_return_empty_on_not_found(self, client):
        response = client.post("/native/v1/offers/stocks", json={"offer_ids": [123456789]})

        assert response.status_code == 200
        assert response.json == {"offers": []}

    @time_machine.travel("2024-04-01", tick=False)
    def test_return_offers_stocks(self, client):
        extra_data = {
            "allocineId": 12345,
            "author": "mandibule",
            "ean": "3838",
            "musicSubType": "502",
            "musicType": "501",
            "performer": "interprète",
            "showSubType": "101",
            "showType": "100",
            "stageDirector": "metteur en scène",
            "speaker": "intervenant",
            "visa": "vasi",
            "genres": ["ACTION", "DRAMA"],
            "cast": ["cast1", "cast2"],
            "editeur": "editeur",
            "gtl_id": "01030000",
            "releaseDate": "2020-01-01",
            "certificate": "Interdit aux moins de 18 ans",
        }
        offer = offers_factories.OfferFactory(
            subcategoryId=subcategories.SEANCE_CINE.id,
            name="l'offre du siècle",
            extraData=extra_data,
            durationMinutes=33,
        )
        offers_factories.MediationFactory(id=111, offer=offer, thumbCount=1, credit="street credit")
        bookable_stock = offers_factories.EventStockFactory(
            offer=offer,
            price=12.34,
            quantity=2,
            priceCategory__priceCategoryLabel__label="bookable",
            features=[
                cinema_providers_constants.ShowtimeFeatures.VF.value,
                cinema_providers_constants.ShowtimeFeatures.THREE_D.value,
                cinema_providers_constants.ShowtimeFeatures.ICE.value,
            ],
        )
        another_bookable_stock = offers_factories.EventStockFactory(
            offer=offer,
            price=12.34,
            quantity=3,
            priceCategory=bookable_stock.priceCategory,
            features=[
                cinema_providers_constants.ShowtimeFeatures.VO.value,
                cinema_providers_constants.ShowtimeFeatures.THREE_D.value,
            ],
        )
        expired_stock = offers_factories.EventStockFactory(
            offer=offer,
            price=45.67,
            beginningDatetime=datetime.utcnow() - timedelta(days=1),
            priceCategory__priceCategoryLabel__label="expired",
            features=[
                cinema_providers_constants.ShowtimeFeatures.VF.value,
                cinema_providers_constants.ShowtimeFeatures.ICE.value,
            ],
        )
        exhausted_stock = offers_factories.EventStockFactory(
            offer=offer,
            price=89.00,
            quantity=1,
            priceCategory__priceCategoryLabel__label="exhausted",
            features=[cinema_providers_constants.ShowtimeFeatures.VO.value],
        )
        BookingFactory(stock=bookable_stock, user__deposit__expirationDate=datetime(year=2031, month=12, day=31))
        BookingFactory(stock=exhausted_stock, user__deposit__expirationDate=datetime(year=2031, month=12, day=31))
        payload = {"offer_ids": [offer.id]}
        with assert_num_queries(1):
            response = client.post("/native/v1/offers/stocks", json=payload)
        # For the test to be deterministic
        response_offer = response.json["offers"][0]
        response_offer["stocks"].sort(key=lambda stock: stock["id"])

        assert response.status_code == 200
        assert response_offer == {
            "durationMinutes": 33,
            "extraData": {
                "allocineId": 12345,
                "author": "mandibule",
                "ean": "3838",
                "durationMinutes": None,
                "musicSubType": "Acid Jazz",
                "musicType": "Jazz",
                "performer": "interprète",
                "showSubType": "Carnaval",
                "showType": "Arts de la rue",
                "speaker": "intervenant",
                "stageDirector": "metteur en scène",
                "visa": "vasi",
                "genres": ["Action", "Drame"],
                "cast": ["cast1", "cast2"],
                "editeur": "editeur",
                "gtlLabels": None,
                "releaseDate": "2020-01-01",
                "certificate": "Interdit aux moins de 18 ans",
                "bookFormat": None,
            },
            "id": offer.id,
            "image": {"credit": "street credit", "url": "http://localhost/storage/thumbs/mediations/N4"},
            "last30DaysBookings": None,
            "name": "l'offre du siècle",
            "stocks": sorted(
                [
                    {
                        "id": bookable_stock.id,
                        "price": 1234,
                        "beginningDatetime": "2024-05-01T00:00:00Z",
                        "bookingLimitDatetime": "2024-04-30T23:00:00Z",
                        "cancellationLimitDatetime": "2024-04-03T00:00:00Z",
                        "features": ["VF", "3D", "ICE"],
                        "isBookable": True,
                        "isForbiddenToUnderage": False,
                        "isSoldOut": False,
                        "isExpired": False,
                        "activationCode": None,
                        "priceCategoryLabel": "bookable",
                        "remainingQuantity": 1,
                    },
                    {
                        "id": another_bookable_stock.id,
                        "price": 1234,
                        "beginningDatetime": "2024-05-01T00:00:00Z",
                        "bookingLimitDatetime": "2024-04-30T23:00:00Z",
                        "cancellationLimitDatetime": "2024-04-03T00:00:00Z",
                        "features": ["VO", "3D"],
                        "isBookable": True,
                        "isForbiddenToUnderage": False,
                        "isSoldOut": False,
                        "isExpired": False,
                        "activationCode": None,
                        "priceCategoryLabel": "bookable",
                        "remainingQuantity": 3,
                    },
                    {
                        "id": expired_stock.id,
                        "price": 4567,
                        "beginningDatetime": "2024-03-31T00:00:00Z",
                        "bookingLimitDatetime": "2024-03-30T23:00:00Z",
                        "cancellationLimitDatetime": "2024-04-01T00:00:00Z",
                        "features": ["VF", "ICE"],
                        "isBookable": False,
                        "isForbiddenToUnderage": False,
                        "isSoldOut": True,
                        "isExpired": True,
                        "activationCode": None,
                        "priceCategoryLabel": "expired",
                        "remainingQuantity": 1000,
                    },
                    {
                        "id": exhausted_stock.id,
                        "price": 8900,
                        "beginningDatetime": "2024-05-01T00:00:00Z",
                        "bookingLimitDatetime": "2024-04-30T23:00:00Z",
                        "cancellationLimitDatetime": "2024-04-03T00:00:00Z",
                        "features": ["VO"],
                        "isBookable": False,
                        "isForbiddenToUnderage": False,
                        "isSoldOut": True,
                        "isExpired": False,
                        "activationCode": None,
                        "priceCategoryLabel": "exhausted",
                        "remainingQuantity": 0,
                    },
                ],
                key=lambda stock: stock["id"],
            ),
        }


class OffersStocksV2Test:
    def test_return_empty_on_empty_request(self, client):
        # 1. select offer
        with assert_num_queries(1):
            response = client.post("/native/v2/offers/stocks", json={"offer_ids": []})
            assert response.status_code == 200

        assert response.json == {"offers": []}

    def test_return_empty_on_not_found(self, client):
        # 1. select offer
        with assert_num_queries(1):
            response = client.post("/native/v2/offers/stocks", json={"offer_ids": [123456789]})
            assert response.status_code == 200

        assert response.json == {"offers": []}

    @time_machine.travel("2020-01-01", tick=False)
    def test_return_offers_stocks(self, client):
        extra_data = {
            "allocineId": 12345,
            "author": "mandibule",
            "ean": "3838",
            "musicSubType": "502",
            "musicType": "501",
            "performer": "interprète",
            "showSubType": "101",
            "showType": "100",
            "stageDirector": "metteur en scène",
            "speaker": "intervenant",
            "visa": "vasi",
            "genres": ["ACTION", "DRAMA"],
            "cast": ["cast1", "cast2"],
            "editeur": "editeur",
            "gtl_id": "01030000",
            "releaseDate": "2020-01-01",
            "certificate": "Déconseillé -12 ans",
        }
        offer = offers_factories.OfferFactory(
            subcategoryId=subcategories.SEANCE_CINE.id,
            name="l'offre du siècle",
            extraData=extra_data,
            durationMinutes=33,
        )
        offers_factories.MediationFactory(id=111, offer=offer, thumbCount=1, credit="street credit")

        bookable_stock = offers_factories.EventStockFactory(
            offer=offer,
            price=12.34,
            quantity=2,
            priceCategory__priceCategoryLabel__label="bookable",
            features=[
                cinema_providers_constants.ShowtimeFeatures.VF.value,
                cinema_providers_constants.ShowtimeFeatures.THREE_D.value,
                cinema_providers_constants.ShowtimeFeatures.ICE.value,
            ],
        )
        another_bookable_stock = offers_factories.EventStockFactory(
            offer=offer,
            price=12.34,
            quantity=3,
            priceCategory=bookable_stock.priceCategory,
            features=[
                cinema_providers_constants.ShowtimeFeatures.VO.value,
                cinema_providers_constants.ShowtimeFeatures.THREE_D.value,
            ],
        )
        expired_stock = offers_factories.EventStockFactory(
            offer=offer,
            price=45.67,
            beginningDatetime=datetime.utcnow() - timedelta(days=1),
            priceCategory__priceCategoryLabel__label="expired",
            features=[
                cinema_providers_constants.ShowtimeFeatures.VF.value,
                cinema_providers_constants.ShowtimeFeatures.ICE.value,
            ],
        )
        exhausted_stock = offers_factories.EventStockFactory(
            offer=offer,
            price=89.00,
            quantity=1,
            priceCategory__priceCategoryLabel__label="exhausted",
            features=[cinema_providers_constants.ShowtimeFeatures.VO.value],
        )

        BookingFactory(stock=bookable_stock, user__deposit__expirationDate=datetime(year=2031, month=12, day=31))
        BookingFactory(stock=exhausted_stock, user__deposit__expirationDate=datetime(year=2031, month=12, day=31))

        payload = {"offer_ids": [offer.id]}

        nb_queries = 1  # select offer
        nb_queries += 1  # select stocks
        nb_queries += 1  # select mediations
        nb_queries += 1  # select chronicles
        nb_queries += 1  # select futureOffer
        with assert_num_queries(nb_queries):
            response = client.post("/native/v2/offers/stocks", json=payload)

        # For the test to be deterministic
        response_offer = response.json["offers"][0]
        response_offer["stocks"].sort(key=lambda stock: stock["id"])

        assert response.status_code == 200

        assert response_offer["id"] == offer.id
        assert response_offer["accessibility"] == {
            "audioDisability": False,
            "mentalDisability": False,
            "motorDisability": False,
            "visualDisability": False,
        }
        assert response_offer["stocks"] == sorted(
            [
                {
                    "id": bookable_stock.id,
                    "price": 1234,
                    "beginningDatetime": "2020-01-31T00:00:00Z",
                    "bookingLimitDatetime": "2020-01-30T23:00:00Z",
                    "cancellationLimitDatetime": "2020-01-03T00:00:00Z",
                    "features": ["VF", "3D", "ICE"],
                    "isBookable": True,
                    "isForbiddenToUnderage": False,
                    "isSoldOut": False,
                    "isExpired": False,
                    "activationCode": None,
                    "priceCategoryLabel": "bookable",
                    "remainingQuantity": 1,
                },
                {
                    "id": another_bookable_stock.id,
                    "price": 1234,
                    "beginningDatetime": "2020-01-31T00:00:00Z",
                    "bookingLimitDatetime": "2020-01-30T23:00:00Z",
                    "cancellationLimitDatetime": "2020-01-03T00:00:00Z",
                    "features": ["VO", "3D"],
                    "isBookable": True,
                    "isForbiddenToUnderage": False,
                    "isSoldOut": False,
                    "isExpired": False,
                    "activationCode": None,
                    "priceCategoryLabel": "bookable",
                    "remainingQuantity": 3,
                },
                {
                    "id": expired_stock.id,
                    "price": 4567,
                    "beginningDatetime": "2019-12-31T00:00:00Z",
                    "bookingLimitDatetime": "2019-12-30T23:00:00Z",
                    "cancellationLimitDatetime": "2020-01-01T00:00:00Z",
                    "features": ["VF", "ICE"],
                    "isBookable": False,
                    "isForbiddenToUnderage": False,
                    "isSoldOut": True,
                    "isExpired": True,
                    "activationCode": None,
                    "priceCategoryLabel": "expired",
                    "remainingQuantity": 1000,
                },
                {
                    "id": exhausted_stock.id,
                    "price": 8900,
                    "beginningDatetime": "2020-01-31T00:00:00Z",
                    "bookingLimitDatetime": "2020-01-30T23:00:00Z",
                    "cancellationLimitDatetime": "2020-01-03T00:00:00Z",
                    "features": ["VO"],
                    "isBookable": False,
                    "isForbiddenToUnderage": False,
                    "isSoldOut": True,
                    "isExpired": False,
                    "activationCode": None,
                    "priceCategoryLabel": "exhausted",
                    "remainingQuantity": 0,
                },
            ],
            key=lambda stock: stock["id"],
        )
        assert response_offer["description"] == offer.description
        assert response_offer["externalTicketOfficeUrl"] is None
        assert response_offer["expenseDomains"] == ["all"]
        assert response_offer["extraData"] == {
            "allocineId": 12345,
            "author": "mandibule",
            "ean": "3838",
            "durationMinutes": 33,
            "musicSubType": "Acid Jazz",
            "musicType": "Jazz",
            "performer": "interprète",
            "showSubType": "Carnaval",
            "showType": "Arts de la rue",
            "speaker": "intervenant",
            "stageDirector": "metteur en scène",
            "visa": "vasi",
            "genres": ["Action", "Drame"],
            "cast": ["cast1", "cast2"],
            "editeur": "editeur",
            "gtlLabels": {
                "label": "Œuvres classiques",
                "level01Label": "Littérature",
                "level02Label": "Œuvres classiques",
                "level03Label": None,
                "level04Label": None,
            },
            "releaseDate": "2020-01-01",
            "certificate": "Déconseillé -12 ans",
            "bookFormat": None,
        }
        assert response_offer["images"] == {
            "recto": {
                "url": "http://localhost/storage/thumbs/mediations/N4",
                "credit": "street credit",
            }
        }
        assert response_offer["isExpired"] is False
        assert response_offer["isForbiddenToUnderage"] is False
        assert response_offer["isSoldOut"] is False
        assert response_offer["isDuo"] is False
        assert response_offer["isEducational"] is False
        assert response_offer["isDigital"] is False
        assert response_offer["isReleased"] is True
        assert response_offer["name"] == "l'offre du siècle"
        assert response_offer["subcategoryId"] == subcategories.SEANCE_CINE.id
        assert response_offer["venue"] == {
            "id": offer.venue.id,
            "address": "1 boulevard Poissonnière",
            "city": "Paris",
            "coordinates": {
                "latitude": 48.87004,
                "longitude": 2.3785,
            },
            "name": offer.venue.name,
            "offerer": {"name": offer.venue.managingOfferer.name},
            "postalCode": "75002",
            "publicName": offer.venue.publicName,
            "isPermanent": False,
            "isOpenToPublic": False,
            "timezone": "Europe/Paris",
            "bannerUrl": offer.venue.bannerUrl,
        }
        assert response_offer["withdrawalDetails"] is None
        assert response_offer["publicationDate"] is None


class SendOfferWebAppLinkTest:
    def test_sendinblue_send_offer_webapp_link_by_email(self, client):
        """
        Test that email can be sent with SiB and that the link does not
        use the redirection domain (not activated by default)
        """
        mail = self.send_request(client)
        assert mail["params"]["OFFER_WEBAPP_LINK"].startswith(settings.WEBAPP_V2_URL)

    @pytest.mark.features(ENABLE_IOS_OFFERS_LINK_WITH_REDIRECTION=True)
    def test_send_offer_webapp_link_by_email_with_redirection_link(self, client):
        """
        Test that the redirection domain is used, once the FF has been
        activated.
        """
        mail = self.send_request(client)
        assert mail["params"]["OFFER_WEBAPP_LINK"].startswith(settings.WEBAPP_V2_REDIRECT_URL)

    def test_send_offer_webapp_link_by_email_not_found(self, client):
        user = users_factories.UserFactory()
        client = client.with_token(user.email)

        with assert_no_duplicated_queries():
            response = client.post("/native/v1/send_offer_webapp_link_by_email/98765432123456789")
            assert response.status_code == 404
        assert not mails_testing.outbox

    @pytest.mark.parametrize(
        "validation", [OfferValidationStatus.DRAFT, OfferValidationStatus.PENDING, OfferValidationStatus.REJECTED]
    )
    def test_send_non_approved_offer_webapp_link_by_email(self, client, validation):
        user = users_factories.UserFactory()
        client = client.with_token(user.email)
        offer_id = offers_factories.OfferFactory(validation=validation).id

        with assert_no_duplicated_queries():
            response = client.post(f"/native/v1/send_offer_webapp_link_by_email/{offer_id}")
            assert response.status_code == 404
        assert not mails_testing.outbox

    def send_request(self, client):
        offer_id = offers_factories.OfferFactory().id
        user = users_factories.BeneficiaryGrant18Factory()
        test_client = client.with_token(user.email)

        with assert_no_duplicated_queries():
            response = test_client.post(f"/native/v1/send_offer_webapp_link_by_email/{offer_id}")
            assert response.status_code == 204

        assert len(mails_testing.outbox) == 1

        mail = mails_testing.outbox[0]
        assert mail["To"] == user.email

        return mail


class SendOfferLinkNotificationTest:
    def test_send_offer_link_notification(self, client):
        """
        Test that a push notification to the user is send with a link to the
        offer.
        """
        # offer.id must be used before the assert_num_queries context manager
        # because it triggers a SQL query.
        offer = offers_factories.OfferFactory()
        offer_id = offer.id

        user = users_factories.UserFactory()
        client = client.with_token(user.email)

        with assert_no_duplicated_queries():
            response = client.post(f"/native/v1/send_offer_link_by_push/{offer_id}")
            assert response.status_code == 204

        assert len(notifications_testing.requests) == 1

        notification = notifications_testing.requests[0]
        assert notification["user_ids"] == [user.id]

        assert offer.name in notification["message"]["title"]

    def test_send_offer_link_notification_not_found(self, client):
        """Test that no push notification is sent when offer is not found"""
        user = users_factories.UserFactory()
        client = client.with_token(user.email)

        with assert_no_duplicated_queries():
            response = client.post("/native/v1/send_offer_link_by_push/9999999999")
            assert response.status_code == 404

        assert len(notifications_testing.requests) == 0

    @pytest.mark.parametrize(
        "validation", [OfferValidationStatus.DRAFT, OfferValidationStatus.PENDING, OfferValidationStatus.REJECTED]
    )
    def test_send_non_approved_offer_link_notification(self, client, validation):
        user = users_factories.UserFactory()
        client = client.with_token(user.email)
        offer_id = offers_factories.OfferFactory(validation=validation).id

        with assert_no_duplicated_queries():
            response = client.post(f"/native/v1/send_offer_link_by_push/{offer_id}")
            assert response.status_code == 404

        assert len(notifications_testing.requests) == 0


class ReportOfferTest:
    def test_report_offer(self, client):
        user = users_factories.UserFactory()
        client = client.with_token(user.email)
        offer = offers_factories.OfferFactory()
        offer_id = offer.id

        # expected queries:
        #   * select offer
        #   * get user
        #   * insert report
        #
        #   * reload user
        #   * select offer
        with assert_num_queries(5):
            response = client.post(f"/native/v1/offer/{offer_id}/report", json={"reason": "INAPPROPRIATE"})
            assert response.status_code == 204

        assert OfferReport.query.count() == 1
        report = OfferReport.query.first()

        assert report.user == user
        assert report.offer == offer

        assert len(mails_testing.outbox) == 1

        email = mails_testing.outbox[0]
        assert email["To"] == "report_offer@example.com"
        assert email["params"]["USER_ID"] == user.id
        assert email["params"]["OFFER_ID"] == offer.id

    def test_report_offer_with_custom_reason(self, client):
        user = users_factories.UserFactory()
        client = client.with_token(user.email)
        offer = offers_factories.OfferFactory()
        offer_id = offer.id

        # expected queries:
        #   * select offer
        #   * get user
        #   * insert report
        #
        #   * reload user
        #   * select offer
        with assert_num_queries(5):
            data = {"reason": "OTHER", "customReason": "saynul"}
            response = client.post(f"/native/v1/offer/{offer_id}/report", json=data)
            assert response.status_code == 204

        assert OfferReport.query.count() == 1
        report = OfferReport.query.first()

        assert report.user == user
        assert report.offer == offer

        assert len(mails_testing.outbox) == 1

        email = mails_testing.outbox[0]
        assert email["To"] == "support@example.com"
        assert email["params"]["USER_ID"] == user.id
        assert email["params"]["OFFER_ID"] == offer.id
        assert "saynul" in email["params"]["REASON"]
        assert "OFFER_URL" in email["params"]

    def test_report_offer_twice(self, client):
        user = users_factories.UserFactory()
        client = client.with_token(user.email)
        offer = offers_factories.OfferFactory()

        offers_factories.OfferReportFactory(user=user, offer=offer)

        with assert_no_duplicated_queries():
            response = client.post(f"/native/v1/offer/{offer.id}/report", json={"reason": "PRICE_TOO_HIGH"})
            assert response.status_code == 400
            assert response.json["code"] == "OFFER_ALREADY_REPORTED"

        assert OfferReport.query.count() == 1  # no new report
        assert not mails_testing.outbox

    def test_report_offer_malformed(self, app, client):
        user = UserFactory()
        offer = offers_factories.OfferFactory()

        # user.email triggers an SQL request, same for offer.id
        # therefore, these attributes should be read outside of the
        # assert_num_queries() block
        email = user.email
        offer_id = offer.id

        with assert_no_duplicated_queries():
            dst = f"/native/v1/offer/{offer_id}/report"
            response = client.with_token(email).post(dst, json={"reason": "OTHER"})
            assert response.status_code == 400
            assert response.json["code"] == "REPORT_MALFORMED"

        assert OfferReport.query.count() == 0  # no new report
        assert not mails_testing.outbox

    def test_report_offer_custom_reason_too_long(self, app, client):
        offer = offers_factories.OfferFactory()
        offer_id = offer.id

        with assert_num_queries(0):
            data = {"reason": "OTHER", "customReason": "a" * 513}
            response = client.post(f"/native/v1/offer/{offer_id}/report", json=data)
            assert response.status_code == 400
            assert response.json["customReason"] == ["custom reason is too long"]

        assert OfferReport.query.count() == 0  # no new report
        assert not mails_testing.outbox

    def test_report_offer_unknown_reason(self, app, client):
        offer = offers_factories.OfferFactory()
        offer_id = offer.id

        with assert_num_queries(0):
            data = {"reason": "UNKNOWN"}
            response = client.post(f"/native/v1/offer/{offer_id}/report", json=data)
            assert response.status_code == 400
            assert response.json["reason"] == [
                "value is not a valid enumeration member; permitted: 'IMPROPER', 'PRICE_TOO_HIGH', 'INAPPROPRIATE', 'OTHER'"
            ]

        assert OfferReport.query.count() == 0  # no new report
        assert not mails_testing.outbox

    @pytest.mark.parametrize(
        "validation", [OfferValidationStatus.DRAFT, OfferValidationStatus.PENDING, OfferValidationStatus.REJECTED]
    )
    def test_report_non_approved_offer(self, client, validation):
        user = users_factories.UserFactory()
        offer = offers_factories.ThingOfferFactory(validation=validation)

        response = client.with_token(user.email).post(
            f"/native/v1/offer/{offer.id}/report", json={"reason": "PRICE_TOO_HIGH"}
        )

        assert response.status_code == 404
        assert OfferReport.query.count() == 0  # no new report
        assert not mails_testing.outbox


class OfferReportReasonsTest:
    def test_get_reasons(self, app, client):
        user = UserFactory()
        response = client.with_token(user.email).get("/native/v1/offer/report/reasons")

        assert response.status_code == 200
        assert response.json["reasons"] == {
            "IMPROPER": {
                "title": "La description est non conforme",
                "description": "La date ne correspond pas, mauvaise description...",
            },
            "PRICE_TOO_HIGH": {"title": "Le tarif est trop élevé", "description": "comparé à l'offre publique"},
            "INAPPROPRIATE": {
                "title": "Le contenu est inapproprié",
                "description": "violence, incitation à la haine, nudité...",
            },
            "OTHER": {"title": "Autre", "description": ""},
        }


class ReportedOffersTest:
    def test_get_user_reported_offers(self, client):
        user = UserFactory()
        offers = offers_factories.OfferFactory.create_batch(3)
        reports = [
            offers_factories.OfferReportFactory(user=user, offer=offers[0]),
            offers_factories.OfferReportFactory(user=user, offer=offers[1]),
        ]

        # offers reported by this user should not be returned
        another_user = UserFactory()
        offers_factories.OfferReportFactory(user=another_user, offer=offers[2])

        client.with_token(user.email)
        with assert_num_queries(2):  # user + offer reports
            response = client.get("/native/v1/offers/reports")
            assert response.status_code == 200

        response_reports = sorted(response.json["reportedOffers"], key=lambda x: x["offerId"])
        assert response_reports == [
            {
                "offerId": reports[0].offerId,
                "reportedAt": reports[0].reportedAt.isoformat(),
                "reason": reports[0].reason.value,
            },
            {
                "offerId": reports[1].offerId,
                "reportedAt": reports[1].reportedAt.isoformat(),
                "reason": reports[1].reason.value,
            },
        ]

    def test_get_no_reported_offers(self, client):
        user = UserFactory()
        offers_factories.OfferFactory()

        client.with_token(user.email)
        with assert_num_queries(2):  # user + offer reports
            response = client.get("/native/v1/offers/reports")
            assert response.status_code == 200

        assert not response.json["reportedOffers"]


class SubcategoriesTest:
    def test_get_subcategories_v2(self, client):
        with assert_num_queries(0):
            response = client.get("/native/v1/subcategories/v2")

        assert response.status_code == 200

        assert set(response.json.keys()) == {
            "subcategories",
            "searchGroups",
            "homepageLabels",
            "nativeCategories",
            "genreTypes",
        }

        found_subcategory_ids = {x["id"] for x in response.json["subcategories"]}
        expected_subcategory_ids = {x.id for x in subcategories.ALL_SUBCATEGORIES}
        assert found_subcategory_ids == expected_subcategory_ids

        found_search_group_names = {x["name"] for x in response.json["searchGroups"]}
        expected_search_group_names = {x.name for x in app_search_tree.SEARCH_GROUPS}
        assert found_search_group_names == expected_search_group_names

        found_home_labels = {x["name"] for x in response.json["homepageLabels"]}
        expected_home_labels = {x.homepage_label_name for x in subcategories.ALL_SUBCATEGORIES}
        assert found_home_labels == expected_home_labels

        found_native_categories = {x["name"] for x in response.json["nativeCategories"]}
        expected_native_categories = {x.name for x in app_search_tree.NATIVE_CATEGORIES}
        assert found_native_categories == expected_native_categories

        found_genre_types = {x["name"] for x in response.json["genreTypes"]}
        expected_genre_types = {x.name for x in categories_models.GenreType}
        assert found_genre_types == expected_genre_types

    def test_genre_types(self, client):
        with assert_num_queries(0):
            response = client.get("/native/v1/subcategories/v2")

        genreTypes = response.json["genreTypes"]
        assert genreTypes == [
            {
                "name": "BOOK",
                "values": [
                    {"name": "Art", "value": "Art"},
                    {"name": "Arts Culinaires", "value": "Arts Culinaires"},
                    {"name": "Bandes dessinées", "value": "Bandes dessinées"},
                    {"name": "Carrière/Concours", "value": "Carrière/Concours"},
                    {"name": "Droit", "value": "Droit"},
                    {"name": "Faits, témoignages", "value": "Faits, témoignages"},
                    {"name": "Gestion/entreprise", "value": "Gestion/entreprise"},
                    {"name": "Géographie, cartographie", "value": "Géographie, cartographie"},
                    {"name": "Histoire", "value": "Histoire"},
                    {"name": "Humour", "value": "Humour"},
                    {"name": "Informatique", "value": "Informatique"},
                    {"name": "Jeunesse", "value": "Jeunesse"},
                    {"name": "Jeux", "value": "Jeux"},
                    {"name": "Langue", "value": "Langue"},
                    {"name": "Littérature Européenne", "value": "Littérature Européenne"},
                    {"name": "Littérature française", "value": "Littérature française"},
                    {"name": "Littérature étrangère", "value": "Littérature étrangère"},
                    {"name": "Loisirs", "value": "Loisirs"},
                    {"name": "Manga", "value": "Manga"},
                    {"name": "Marketing et audio-visuel", "value": "Marketing et audio-visuel"},
                    {"name": "Policier", "value": "Policier"},
                    {"name": "Poésie, théâtre et spectacle", "value": "Poésie, théâtre et spectacle"},
                    {"name": "Psychanalyse, psychologie", "value": "Psychanalyse, psychologie"},
                    {"name": "Religions, spiritualités", "value": "Religions, spiritualités"},
                    {"name": "Santé", "value": "Santé"},
                    {
                        "name": "Science-fiction, fantastique & terreur",
                        "value": "Science-fiction, fantastique & terreur",
                    },
                    {
                        "name": "Sciences Humaines, Encyclopédie, dictionnaire",
                        "value": "Sciences Humaines, Encyclopédie, dictionnaire",
                    },
                    {"name": "Sciences, vie & Nature", "value": "Sciences, vie & Nature"},
                    {"name": "Scolaire & Parascolaire", "value": "Scolaire & Parascolaire"},
                    {"name": "Sexualité", "value": "Sexualité"},
                    {"name": "Sociologie", "value": "Sociologie"},
                    {"name": "Sport", "value": "Sport"},
                    {"name": "Tourisme", "value": "Tourisme"},
                    {"name": "Vie pratique", "value": "Vie pratique"},
                    {"name": "Économie", "value": "Économie"},
                ],
                "trees": [
                    {
                        "children": [
                            {
                                "label": "Romance",
                                "gtls": [
                                    {"code": "01020600", "label": "Roman sentimental", "level": 3},
                                    {"code": "92000000", "label": "Romance", "level": 1},
                                ],
                                "position": 1,
                            },
                            {
                                "label": "Thriller",
                                "gtls": [
                                    {"code": "01020500", "label": "Thriller", "level": 3},
                                    {"code": "90020000", "label": "Thriller", "level": 2},
                                ],
                                "position": 2,
                            },
                            {
                                "label": "Fantasy",
                                "gtls": [
                                    {"code": "01020900", "label": "Fantasy", "level": 3},
                                    {"code": "91030000", "label": "Fantasy", "level": 2},
                                ],
                                "position": 3,
                            },
                            {
                                "label": "Policier",
                                "gtls": [
                                    {"code": "01020400", "label": "Policier", "level": 3},
                                    {"code": "90010000", "label": "Policier", "level": 2},
                                ],
                                "position": 4,
                            },
                            {
                                "label": "Œuvres classiques",
                                "gtls": [{"code": "01030000", "label": "Œuvres classiques", "level": 2}],
                                "position": 5,
                            },
                            {
                                "label": "Science-fiction",
                                "gtls": [
                                    {"code": "01020700", "label": "Science-fiction", "level": 3},
                                    {"code": "91010000", "label": "Science-fiction", "level": 2},
                                ],
                                "position": 6,
                            },
                            {
                                "label": "Horreur",
                                "gtls": [
                                    {"code": "01020802", "label": "Horreur / Terreur", "level": 4},
                                    {"code": "91020200", "label": "Horreur / Terreur", "level": 3},
                                ],
                                "position": 7,
                            },
                            {
                                "label": "Aventure",
                                "gtls": [
                                    {"code": "01020200", "label": "Aventure", "level": 3},
                                    {"code": "01020300", "label": "Espionnage", "level": 3},
                                ],
                                "position": 8,
                            },
                            {
                                "label": "Biographie",
                                "gtls": [
                                    {"code": "01060000", "label": "Biographie / Témoignage littéraire", "level": 2}
                                ],
                                "position": 9,
                            },
                            {
                                "label": "Contes & légendes",
                                "gtls": [{"code": "01040000", "label": "Contes / Légendes", "level": 2}],
                                "position": 10,
                            },
                        ],
                        "gtls": [
                            {"code": "01010000", "label": "Romans & Nouvelles", "level": 2},
                            {"code": "01020000", "label": "Romans & Nouvelles de genre", "level": 2},
                            {"code": "01030000", "label": "Œuvres classiques", "level": 2},
                            {"code": "02000000", "label": "Jeunesse", "level": 1},
                            {"code": "01060000", "label": "Biographie / Témoignage littéraire", "level": 2},
                            {"code": "01040000", "label": "Contes / Légendes", "level": 2},
                            {"code": "92000000", "label": "Romance", "level": 1},
                            {"code": "91000000", "label": "Fantasy & Science-fiction", "level": 1},
                            {"code": "90000000", "label": "Policier & Thriller", "level": 1},
                        ],
                        "label": "Romans & littérature",
                        "position": 1,
                    },
                    {
                        "children": [
                            {
                                "label": "Shonen",
                                "gtls": [{"code": "03040500", "label": "Shonen", "level": 3}],
                                "position": 1,
                            },
                            {
                                "label": "Seinen",
                                "gtls": [{"code": "03040600", "label": "Seinen", "level": 3}],
                                "position": 2,
                            },
                            {
                                "label": "Shôjo",
                                "gtls": [{"code": "03040400", "label": "Shôjo", "level": 3}],
                                "position": 3,
                            },
                            {
                                "label": "Yaoi",
                                "gtls": [{"code": "03040800", "label": "Yaoi", "level": 3}],
                                "position": 4,
                            },
                            {
                                "label": "Kodomo",
                                "gtls": [{"code": "03040300", "label": "Kodomo", "level": 3}],
                                "position": 5,
                            },
                            {
                                "label": "Josei",
                                "gtls": [{"code": "03040700", "label": "Josei", "level": 3}],
                                "position": 6,
                            },
                            {
                                "label": "Yuri",
                                "gtls": [{"code": "03040900", "label": "Yuri", "level": 3}],
                                "position": 7,
                            },
                        ],
                        "gtls": [
                            {"code": "03040300", "label": "Kodomo", "level": 3},
                            {"code": "03040400", "label": "Shôjo", "level": 3},
                            {"code": "03040500", "label": "Shonen", "level": 3},
                            {"code": "03040600", "label": "Seinen", "level": 3},
                            {"code": "03040700", "label": "Josei", "level": 3},
                            {"code": "03040800", "label": "Yaoi", "level": 3},
                            {"code": "03040900", "label": "Yuri", "level": 3},
                        ],
                        "label": "Mangas",
                        "position": 2,
                    },
                    {
                        "children": [
                            {
                                "label": "Humour",
                                "gtls": [
                                    {"code": "03020111", "label": "Humour", "level": 4},
                                    {"code": "03020211", "label": "Humour", "level": 4},
                                    {"code": "03020310", "label": "Humour", "level": 4},
                                    {"code": "03030210", "label": "Humour", "level": 4},
                                    {"code": "03030310", "label": "Humour", "level": 4},
                                    {"code": "03030410", "label": "Humour", "level": 4},
                                    {"code": "03030510", "label": "Humour", "level": 4},
                                    {"code": "03030610", "label": "Humour", "level": 4},
                                    {"code": "03030710", "label": "Humour", "level": 4},
                                ],
                                "position": 1,
                            },
                            {
                                "label": "Action & aventure",
                                "gtls": [
                                    {"code": "03020109", "label": "Action / Aventures", "level": 4},
                                    {"code": "03020209", "label": "Action / Aventures", "level": 4},
                                    {"code": "03020308", "label": "Action / Aventures", "level": 4},
                                    {"code": "03030208", "label": "Action / Aventures", "level": 4},
                                    {"code": "03030308", "label": "Action / Aventures", "level": 4},
                                    {"code": "03030408", "label": "Action / Aventures", "level": 4},
                                    {"code": "03030508", "label": "Action / Aventures", "level": 4},
                                    {"code": "03030608", "label": "Action / Aventures", "level": 4},
                                    {"code": "03030708", "label": "Action / Aventures", "level": 4},
                                ],
                                "position": 2,
                            },
                            {
                                "label": "Fantastique & épouvante",
                                "gtls": [
                                    {"code": "03020206", "label": "Fantastique / Epouvante", "level": 4},
                                    {"code": "03020305", "label": "Fantastique / Epouvante", "level": 4},
                                    {"code": "03030205", "label": "Fantastique / Epouvante", "level": 4},
                                    {"code": "03030305", "label": "Fantastique / Epouvante", "level": 4},
                                    {"code": "03030405", "label": "Fantastique / Epouvante", "level": 4},
                                    {"code": "03030505", "label": "Fantastique / Epouvante", "level": 4},
                                    {"code": "03030605", "label": "Fantastique / Epouvante", "level": 4},
                                    {"code": "03030705", "label": "Fantastique / Epouvante", "level": 4},
                                ],
                                "position": 3,
                            },
                            {
                                "label": "Documentaire & société",
                                "gtls": [
                                    {"code": "03020103", "label": "Documentaire / Société", "level": 4},
                                    {"code": "03020203", "label": "Documentaire / Société", "level": 4},
                                    {"code": "03020302", "label": "Documentaire / Société", "level": 4},
                                    {"code": "03030202", "label": "Documentaire / Société", "level": 4},
                                    {"code": "03030302", "label": "Documentaire / Société", "level": 4},
                                    {"code": "03030402", "label": "Documentaire / Société", "level": 4},
                                    {"code": "03030502", "label": "Documentaire / Société", "level": 4},
                                    {"code": "03030602", "label": "Documentaire / Société", "level": 4},
                                    {"code": "03030702", "label": "Documentaire / Société", "level": 4},
                                ],
                                "position": 4,
                            },
                            {
                                "label": "Fantasy",
                                "gtls": [
                                    {"code": "03020105", "label": "Fantasy", "level": 4},
                                    {"code": "03020205", "label": "Fantasy", "level": 4},
                                    {"code": "03020304", "label": "Fantasy", "level": 4},
                                    {"code": "03030204", "label": "Fantasy", "level": 4},
                                    {"code": "03030304", "label": "Fantasy", "level": 4},
                                    {"code": "03030404", "label": "Fantasy", "level": 4},
                                    {"code": "03030504", "label": "Fantasy", "level": 4},
                                    {"code": "03030604", "label": "Fantasy", "level": 4},
                                    {"code": "03030704", "label": "Fantasy", "level": 4},
                                ],
                                "position": 5,
                            },
                            {
                                "label": "Histoire",
                                "gtls": [
                                    {"code": "03020108", "label": "Histoire", "level": 4},
                                    {"code": "03020208", "label": "Histoire", "level": 4},
                                    {"code": "03020307", "label": "Histoire", "level": 4},
                                    {"code": "03030207", "label": "Histoire", "level": 4},
                                    {"code": "03030307", "label": "Histoire", "level": 4},
                                    {"code": "03030407", "label": "Histoire", "level": 4},
                                    {"code": "03030507", "label": "Histoire", "level": 4},
                                    {"code": "03030607", "label": "Histoire", "level": 4},
                                    {"code": "03030707", "label": "Histoire", "level": 4},
                                ],
                                "position": 6,
                            },
                            {
                                "label": "Policier & thriller",
                                "gtls": [
                                    {"code": "03020107", "label": "Policier / Thriller", "level": 4},
                                    {"code": "03020207", "label": "Policier / Thriller", "level": 4},
                                    {"code": "03020306", "label": "Policier / Thriller", "level": 4},
                                    {"code": "03030206", "label": "Policier / Thriller", "level": 4},
                                    {"code": "03030306", "label": "Policier / Thriller", "level": 4},
                                    {"code": "03030406", "label": "Policier / Thriller", "level": 4},
                                    {"code": "03030506", "label": "Policier / Thriller", "level": 4},
                                    {"code": "03030606", "label": "Policier / Thriller", "level": 4},
                                    {"code": "03030706", "label": "Policier / Thriller", "level": 4},
                                ],
                                "position": 7,
                            },
                            {
                                "label": "Science-fiction",
                                "gtls": [
                                    {"code": "03020104", "label": "Science-fiction", "level": 4},
                                    {"code": "03020204", "label": "Science-fiction", "level": 4},
                                    {"code": "03020303", "label": "Science-fiction", "level": 4},
                                    {"code": "03030203", "label": "Science-fiction", "level": 4},
                                    {"code": "03030303", "label": "Science-fiction", "level": 4},
                                    {"code": "03030403", "label": "Science-fiction", "level": 4},
                                    {"code": "03030503", "label": "Science-fiction", "level": 4},
                                    {"code": "03030603", "label": "Science-fiction", "level": 4},
                                    {"code": "03030703", "label": "Science-fiction", "level": 4},
                                ],
                                "position": 8,
                            },
                            {
                                "label": "Adaptation",
                                "gtls": [
                                    {"code": "03020102", "label": "Adaptation", "level": 4},
                                    {"code": "03020202", "label": "Adaptation", "level": 4},
                                    {"code": "03020301", "label": "Adaptation", "level": 4},
                                    {"code": "03030201", "label": "Adaptation", "level": 4},
                                    {"code": "03030301", "label": "Adaptation", "level": 4},
                                    {"code": "03030401", "label": "Adaptation", "level": 4},
                                    {"code": "03030501", "label": "Adaptation Autre", "level": 4},
                                    {"code": "03030601", "label": "Adaptation", "level": 4},
                                    {"code": "03030701", "label": "Adaptation", "level": 4},
                                ],
                                "position": 9,
                            },
                            {
                                "label": "Western",
                                "gtls": [
                                    {"code": "03020110", "label": "Western", "level": 4},
                                    {"code": "03020210", "label": "Western", "level": 4},
                                    {"code": "03020309", "label": "Western", "level": 4},
                                    {"code": "03030209", "label": "Western", "level": 4},
                                    {"code": "03030309", "label": "Western", "level": 4},
                                    {"code": "03030409", "label": "Western", "level": 4},
                                    {"code": "03030509", "label": "Western", "level": 4},
                                    {"code": "03030609", "label": "Western", "level": 4},
                                    {"code": "03030709", "label": "Western", "level": 4},
                                ],
                                "position": 10,
                            },
                            {
                                "label": "Super héros",
                                "gtls": [{"code": "03030400", "label": "Super Héros", "level": 3}],
                                "position": 11,
                            },
                            {
                                "label": "Strip",
                                "gtls": [{"code": "03030300", "label": "Strip", "level": 3}],
                                "position": 12,
                            },
                        ],
                        "gtls": [
                            {"code": "03020000", "label": "Bandes dessinées", "level": 2},
                            {"code": "03030000", "label": "Comics", "level": 2},
                        ],
                        "label": "BD & comics",
                        "position": 3,
                    },
                    {
                        "children": [
                            {
                                "label": "Vie quotidienne & bien-être",
                                "gtls": [{"code": "04060000", "label": "Vie quotidienne & Bien-être", "level": 2}],
                                "position": 1,
                            },
                            {
                                "label": "Cuisine",
                                "gtls": [{"code": "04030000", "label": "Arts de la table / Gastronomie", "level": 2}],
                                "position": 2,
                            },
                            {
                                "label": "Activités manuelles",
                                "gtls": [{"code": "04050000", "label": "Hobbies", "level": 2}],
                                "position": 3,
                            },
                            {
                                "label": "Jeux",
                                "gtls": [{"code": "04050500", "label": "Jeux", "level": 3}],
                                "position": 4,
                            },
                            {
                                "label": "Sports",
                                "gtls": [{"code": "04070000", "label": "Sports", "level": 2}],
                                "position": 5,
                            },
                            {
                                "label": "Animaux",
                                "gtls": [{"code": "04020000", "label": "Animaux", "level": 2}],
                                "position": 6,
                            },
                            {
                                "label": "Nature & plein air",
                                "gtls": [{"code": "04010000", "label": "Nature & Plein air", "level": 2}],
                                "position": 7,
                            },
                            {
                                "label": "Habitat & maison",
                                "gtls": [{"code": "04040000", "label": "Habitat / Maison", "level": 2}],
                                "position": 8,
                            },
                            {
                                "label": "Transports",
                                "gtls": [{"code": "04050700", "label": "Transports", "level": 3}],
                                "position": 9,
                            },
                        ],
                        "gtls": [{"code": "04000000", "label": "Vie pratique & Loisirs", "level": 1}],
                        "label": "Loisirs & bien-être",
                        "position": 4,
                    },
                    {
                        "children": [
                            {
                                "label": "Philosophie",
                                "gtls": [{"code": "09080000", "label": "Philosophie", "level": 2}],
                                "position": 1,
                            },
                            {
                                "label": "Sciences politiques",
                                "gtls": [{"code": "09110000", "label": "Sciences politiques & Politique", "level": 2}],
                                "position": 2,
                            },
                            {
                                "label": "Sciences sociales & société",
                                "gtls": [{"code": "09120000", "label": "Sciences sociales  / Société", "level": 2}],
                                "position": 3,
                            },
                            {
                                "label": "Psychologie & psychanalyse",
                                "gtls": [{"code": "09090000", "label": "Psychologie / Psychanalyse", "level": 2}],
                                "position": 4,
                            },
                            {
                                "label": "Actualité & reportage",
                                "gtls": [{"code": "01110000", "label": "Actualités & Reportages", "level": 2}],
                                "position": 5,
                            },
                            {
                                "label": "Anthropologie & ethnologie",
                                "gtls": [
                                    {"code": "09010000", "label": "Anthropologie", "level": 2},
                                    {"code": "09020000", "label": "Ethnologie", "level": 2},
                                ],
                                "position": 6,
                            },
                        ],
                        "gtls": [
                            {"code": "09000000", "label": "Sciences humaines & sociales", "level": 1},
                            {"code": "01110000", "label": "Actualités & Reportages", "level": 2},
                        ],
                        "label": "Société & politique",
                        "position": 5,
                    },
                    {
                        "children": [
                            {
                                "label": "Théâtre",
                                "gtls": [{"code": "01080000", "label": "Théâtre", "level": 2}],
                                "position": 1,
                            },
                            {
                                "label": "Poésie",
                                "gtls": [{"code": "01090000", "label": "Poésie", "level": 2}],
                                "position": 2,
                            },
                            {
                                "label": "Essais littéraires",
                                "gtls": [{"code": "01070000", "label": "Littérature argumentative", "level": 2}],
                                "position": 3,
                            },
                            {
                                "label": "Récit",
                                "gtls": [{"code": "01050000", "label": "Récit", "level": 2}],
                                "position": 4,
                            },
                        ],
                        "gtls": [
                            {"code": "01080000", "label": "Théâtre", "level": 2},
                            {"code": "01090000", "label": "Poésie", "level": 2},
                            {"code": "01070000", "label": "Littérature argumentative", "level": 2},
                            {"code": "01050000", "label": "Récit", "level": 2},
                        ],
                        "label": "Théâtre, poésie & essais",
                        "position": 6,
                    },
                    {
                        "children": [
                            {
                                "label": "Droit",
                                "gtls": [{"code": "08030000", "label": "Droit", "level": 2}],
                                "position": 1,
                            },
                            {
                                "label": "Médecine",
                                "gtls": [{"code": "10080000", "label": "Médecine", "level": 2}],
                                "position": 2,
                            },
                            {
                                "label": "Entreprise",
                                "gtls": [
                                    {"code": "08040000", "label": "Entreprise, gestion et management", "level": 2}
                                ],
                                "position": 3,
                            },
                            {
                                "label": "Sciences économiques",
                                "gtls": [{"code": "08010000", "label": "Sciences économiques", "level": 2}],
                                "position": 4,
                            },
                            {
                                "label": "Histoire",
                                "gtls": [
                                    {"code": "09050000", "label": "Histoire", "level": 2},
                                    {"code": "09060000", "label": "Histoire du monde", "level": 2},
                                ],
                                "position": 5,
                            },
                            {
                                "label": "Géographie",
                                "gtls": [
                                    {"code": "09030000", "label": "Géographie", "level": 2},
                                    {"code": "09040000", "label": "Géographie du monde", "level": 2},
                                ],
                                "position": 6,
                            },
                            {
                                "label": "Sciences de la Terre et de l’Univers",
                                "gtls": [
                                    {"code": "10050000", "label": "Sciences de la Terre et de l'Univers", "level": 2}
                                ],
                                "position": 7,
                            },
                            {
                                "label": "Physiques, mathématiques & informatique",
                                "gtls": [
                                    {"code": "10030000", "label": "Sciences physiques", "level": 2},
                                    {"code": "10020000", "label": "Mathématiques", "level": 2},
                                    {"code": "10070000", "label": "Informatique", "level": 2},
                                ],
                                "position": 8,
                            },
                            {
                                "label": "Sciences appliquées & industrie",
                                "gtls": [{"code": "10060000", "label": "Sciences appliquées et industrie", "level": 2}],
                                "position": 9,
                            },
                            {
                                "label": "Dictionnaires",
                                "gtls": [{"code": "13010000", "label": "Dictionnaires de français", "level": 2}],
                                "position": 10,
                            },
                            {
                                "label": "Encyclopédies",
                                "gtls": [{"code": "13020000", "label": "Encyclopédies", "level": 2}],
                                "position": 11,
                            },
                        ],
                        "gtls": [
                            {"code": "08030000", "label": "Droit", "level": 2},
                            {"code": "10080000", "label": "Médecine", "level": 2},
                            {"code": "08040000", "label": "Entreprise, gestion et management", "level": 2},
                            {"code": "08010000", "label": "Sciences économiques", "level": 2},
                            {"code": "09050000", "label": "Histoire", "level": 2},
                            {"code": "09060000", "label": "Histoire du monde", "level": 2},
                            {"code": "09030000", "label": "Géographie", "level": 2},
                            {"code": "09040000", "label": "Géographie du monde", "level": 2},
                            {"code": "10050000", "label": "Sciences de la Terre et de l'Univers", "level": 2},
                            {"code": "10030000", "label": "Sciences physiques", "level": 2},
                            {"code": "10020000", "label": "Mathématiques", "level": 2},
                            {"code": "10070000", "label": "Informatique", "level": 2},
                            {"code": "10060000", "label": "Sciences appliquées et industrie", "level": 2},
                            {"code": "13010000", "label": "Dictionnaires de français", "level": 2},
                            {"code": "13020000", "label": "Encyclopédies", "level": 2},
                        ],
                        "label": "Compétences générales",
                        "position": 7,
                    },
                    {
                        "children": [
                            {
                                "label": "Mode",
                                "gtls": [{"code": "06100200", "label": "Mode / Parfums / Cosmétiques", "level": 3}],
                                "position": 1,
                            },
                            {
                                "label": "Peinture, sculpture & arts graphiques",
                                "gtls": [
                                    {"code": "06100100", "label": "Arts appliqués / Arts décoratifs autre", "level": 3},
                                    {"code": "06100300", "label": "Décoration d'intérieur", "level": 3},
                                    {"code": "06100400", "label": "Métiers d'art", "level": 3},
                                    {"code": "06100500", "label": "Techniques / Enseignement", "level": 3},
                                    {"code": "06050000", "label": "Peinture / Arts graphiques", "level": 2},
                                    {"code": "06060000", "label": "Sculpture / Arts plastiques", "level": 2},
                                ],
                                "position": 2,
                            },
                            {
                                "label": "Photos & cinéma",
                                "gtls": [{"code": "06070000", "label": "Arts de l'image", "level": 2}],
                                "position": 3,
                            },
                            {
                                "label": "Architecture, urbanisme & design",
                                "gtls": [{"code": "06040000", "label": "Architecture / Urbanisme", "level": 2}],
                                "position": 4,
                            },
                            {
                                "label": "Musique",
                                "gtls": [{"code": "06030000", "label": "Musique", "level": 2}],
                                "position": 5,
                            },
                        ],
                        "gtls": [{"code": "06000000", "label": "Arts et spectacles", "level": 1}],
                        "label": "Mode & art",
                        "position": 8,
                    },
                    {
                        "children": [
                            {
                                "label": "Monde",
                                "gtls": [{"code": "05030000", "label": "Tourisme & Voyages Monde", "level": 2}],
                                "position": 1,
                            },
                            {
                                "label": "France",
                                "gtls": [{"code": "05020000", "label": "Tourisme & Voyages France", "level": 2}],
                                "position": 2,
                            },
                            {
                                "label": "Europe",
                                "gtls": [{"code": "05040000", "label": "Tourisme & Voyages Europe", "level": 2}],
                                "position": 3,
                            },
                            {
                                "label": "Asie",
                                "gtls": [{"code": "05100000", "label": "Tourisme & Voyages Asie", "level": 2}],
                                "position": 4,
                            },
                            {
                                "label": "Amérique du Nord",
                                "gtls": [
                                    {"code": "05070000", "label": "Tourisme & Voyages Amérique du Nord", "level": 2}
                                ],
                                "position": 5,
                            },
                            {
                                "label": "Afrique",
                                "gtls": [{"code": "05060000", "label": "Tourisme & Voyages Afrique", "level": 2}],
                                "position": 6,
                            },
                            {
                                "label": "Océanie",
                                "gtls": [{"code": "05110000", "label": "Tourisme & Voyages Océanie", "level": 2}],
                                "position": 7,
                            },
                            {
                                "label": "Arctique & Antarctique",
                                "gtls": [
                                    {
                                        "code": "05120000",
                                        "label": "Tourisme & Voyages Arctique / Antarctique",
                                        "level": 2,
                                    }
                                ],
                                "position": 8,
                            },
                            {
                                "label": "Amérique centrale & Caraïbes",
                                "gtls": [
                                    {
                                        "code": "05080000",
                                        "label": "Tourisme & Voyages Amérique centrale et Caraïbes",
                                        "level": 2,
                                    }
                                ],
                                "position": 9,
                            },
                            {
                                "label": "Amérique du Sud",
                                "gtls": [
                                    {"code": "05090000", "label": "Tourisme & Voyages Amérique du Sud", "level": 2}
                                ],
                                "position": 10,
                            },
                            {
                                "label": "Moyen-Orient",
                                "gtls": [{"code": "05050000", "label": "Tourisme & Voyages Moyen-Orient", "level": 2}],
                                "position": 11,
                            },
                        ],
                        "gtls": [{"code": "05000000", "label": "Tourisme & Voyages", "level": 1}],
                        "label": "Tourisme & voyages",
                        "position": 9,
                    },
                ],
            },
            {
                "name": "MUSIC",
                "values": [
                    {"name": "ALTERNATIF", "value": "Alternatif"},
                    {"name": "AMBIANCE", "value": "Ambiance"},
                    {"name": "AUTRES", "value": "Autre"},
                    {"name": "BANDES_ORIGINALES", "value": "Bandes originales"},
                    {"name": "COMPILATIONS", "value": "Compilations"},
                    {"name": "COUNTRY-FOLK", "value": "Country / Folk"},
                    {"name": "ELECTRO", "value": "Electro"},
                    {"name": "ENFANTS", "value": "Enfants"},
                    {"name": "FUNK-SOUL-RNB-DISCO", "value": "Funk / Soul / RnB / Disco"},
                    {"name": "JAZZ-BLUES", "value": "Jazz / Blues"},
                    {"name": "METAL", "value": "Metal"},
                    {"name": "MUSIQUE_CLASSIQUE", "value": "Musique Classique"},
                    {"name": "MUSIQUE_DU_MONDE", "value": "Musique du monde"},
                    {"name": "POP", "value": "Pop"},
                    {"name": "RAP-HIP HOP", "value": "Rap / Hip Hop"},
                    {"name": "REGGAE-RAGGA", "value": "Reggae / Ragga"},
                    {"name": "ROCK", "value": "Rock"},
                    {"name": "VARIETES", "value": "Variétés"},
                    {"name": "VIDEOS_MUSICALES", "value": "Vidéos musicales"},
                ],
                "trees": [
                    {"label": "Musique Classique", "name": "MUSIQUE_CLASSIQUE"},
                    {"label": "Jazz / Blues", "name": "JAZZ-BLUES"},
                    {"label": "Bandes originales", "name": "BANDES_ORIGINALES"},
                    {"label": "Electro", "name": "ELECTRO"},
                    {"label": "Pop", "name": "POP"},
                    {"label": "Rock", "name": "ROCK"},
                    {"label": "Metal", "name": "METAL"},
                    {"label": "Alternatif", "name": "ALTERNATIF"},
                    {"label": "Variétés", "name": "VARIETES"},
                    {"label": "Funk / Soul / RnB / Disco", "name": "FUNK-SOUL-RNB-DISCO"},
                    {"label": "Rap / Hip Hop", "name": "RAP-HIP HOP"},
                    {"label": "Reggae / Ragga", "name": "REGGAE-RAGGA"},
                    {"label": "Musique du monde", "name": "MUSIQUE_DU_MONDE"},
                    {"label": "Country / Folk", "name": "COUNTRY-FOLK"},
                    {"label": "Vidéos musicales", "name": "VIDEOS_MUSICALES"},
                    {"label": "Compilations", "name": "COMPILATIONS"},
                    {"label": "Ambiance", "name": "AMBIANCE"},
                    {"label": "Enfants", "name": "ENFANTS"},
                    {"label": "Autre", "name": "AUTRES"},
                ],
            },
            {
                "name": "SHOW",
                "values": [
                    {"name": "Arts de la rue", "value": "Arts de la rue"},
                    {"name": "Autre", "value": "Autre"},
                    {
                        "name": "Autre (spectacle sur glace, historique, aquatique, …)  ",
                        "value": "Autre (spectacle sur glace, historique, aquatique, …)  ",
                    },
                    {"name": "Cirque", "value": "Cirque"},
                    {"name": "Danse", "value": "Danse"},
                    {"name": "Humour / Café-théâtre", "value": "Humour / Café-théâtre"},
                    {"name": "Opéra", "value": "Opéra"},
                    {"name": "Pluridisciplinaire", "value": "Pluridisciplinaire"},
                    {"name": "Spectacle Jeunesse", "value": "Spectacle Jeunesse"},
                    {
                        "name": "Spectacle Musical / Cabaret / Opérette",
                        "value": "Spectacle Musical / Cabaret / Opérette",
                    },
                    {"name": "Théâtre", "value": "Théâtre"},
                ],
                "trees": [
                    {
                        "children": [
                            {"code": 101, "label": "Carnaval", "slug": "ART_DE_LA_RUE-CARNAVAL"},
                            {"code": 102, "label": "Fanfare", "slug": "ART_DE_LA_RUE-FANFARE"},
                            {"code": 103, "label": "Mime", "slug": "ART_DE_LA_RUE-MIME"},
                            {"code": 104, "label": "Parade", "slug": "ART_DE_LA_RUE-PARADE"},
                            {"code": 105, "label": "Théâtre de Rue", "slug": "ART_DE_LA_RUE-THEATRE_DE_RUE"},
                            {"code": 106, "label": "Théâtre Promenade", "slug": "ART_DE_LA_RUE-THEATRE_PROMENADE"},
                            {"code": -1, "label": "Autre", "slug": "ART_DE_LA_RUE-OTHER"},
                        ],
                        "code": 100,
                        "label": "Arts de la rue",
                    },
                    {
                        "children": [
                            {"code": 201, "label": "Cirque Contemporain", "slug": "CIRQUE-CIRQUE_CONTEMPORAIN"},
                            {"code": 202, "label": "Cirque Hors les murs", "slug": "CIRQUE-CIRQUE_HORS_LES_MURS"},
                            {"code": 203, "label": "Cirque Traditionel", "slug": "CIRQUE-CIRQUE_TRADITIONNEL"},
                            {"code": 204, "label": "Cirque Voyageur", "slug": "CIRQUE-CIRQUE_VOYAGEUR"},
                            {"code": 205, "label": "Clown", "slug": "CIRQUE-CLOWN"},
                            {"code": 206, "label": "Hypnose", "slug": "CIRQUE-HYPNOSE"},
                            {"code": 207, "label": "Mentaliste", "slug": "CIRQUE-MENTALISTE"},
                            {"code": 208, "label": "Spectacle de Magie", "slug": "CIRQUE-SPECTACLE_DE_MAGIE"},
                            {"code": 209, "label": "Spectacle Équestre", "slug": "CIRQUE-SPECTACLE_EQUESTRE"},
                            {"code": -1, "label": "Autre", "slug": "CIRQUE-OTHER"},
                        ],
                        "code": 200,
                        "label": "Cirque",
                    },
                    {
                        "children": [
                            {"code": 302, "label": "Ballet", "slug": "DANSE-BALLET"},
                            {"code": 303, "label": "Cancan", "slug": "DANSE-CANCAN"},
                            {"code": 304, "label": "Claquette", "slug": "DANSE-CLAQUETTE"},
                            {"code": 305, "label": "Classique", "slug": "DANSE-CLASSIQUE"},
                            {"code": 306, "label": "Contemporaine", "slug": "DANSE-CONTEMPORAINE"},
                            {"code": 307, "label": "Danse du Monde", "slug": "DANSE-DANSE_DU_MONDE"},
                            {"code": 308, "label": "Flamenco", "slug": "DANSE-FLAMENCO"},
                            {"code": 309, "label": "Moderne Jazz", "slug": "DANSE-MODERNE_JAZZ"},
                            {"code": 311, "label": "Salsa", "slug": "DANSE-SALSA"},
                            {"code": 312, "label": "Swing", "slug": "DANSE-SWING"},
                            {"code": 313, "label": "Tango", "slug": "DANSE-TANGO"},
                            {"code": 314, "label": "Urbaine", "slug": "DANSE-URBAINE"},
                            {"code": -1, "label": "Autre", "slug": "DANSE-OTHER"},
                        ],
                        "code": 300,
                        "label": "Danse",
                    },
                    {
                        "children": [
                            {"code": 401, "label": "Café Théâtre", "slug": "HUMOUR-CAFE_THEATRE"},
                            {"code": 402, "label": "Improvisation", "slug": "HUMOUR-IMPROVISATION"},
                            {"code": 403, "label": "Seul.e en scène", "slug": "HUMOUR-SEUL_EN_SCENE"},
                            {"code": 404, "label": "Sketch", "slug": "HUMOUR-SKETCH"},
                            {"code": 405, "label": "Stand Up", "slug": "HUMOUR-STAND_UP"},
                            {"code": 406, "label": "Ventriloque", "slug": "HUMOUR-VENTRILOQUE"},
                            {"code": -1, "label": "Autre", "slug": "HUMOUR-OTHER"},
                        ],
                        "code": 400,
                        "label": "Humour / Café-théâtre",
                    },
                    {
                        "children": [
                            {"code": 1101, "label": "Cabaret", "slug": "SPECTACLE_MUSICAL-CABARET"},
                            {"code": 1102, "label": "Café Concert", "slug": "SPECTACLE_MUSICAL-CAFE_CONCERT"},
                            {"code": 1103, "label": "Claquette", "slug": "SPECTACLE_MUSICAL-CLAQUETTE"},
                            {"code": 1104, "label": "Comédie Musicale", "slug": "SPECTACLE_MUSICAL-COMEDIE_MUSICALE"},
                            {"code": 1105, "label": "Opéra Bouffe", "slug": "SPECTACLE_MUSICAL-OPERA_BOUFFE"},
                            {"code": 1108, "label": "Opérette", "slug": "SPECTACLE_MUSICAL-OPERETTE"},
                            {"code": 1109, "label": "Revue", "slug": "SPECTACLE_MUSICAL-REVUE"},
                            {"code": 1111, "label": "Burlesque", "slug": "SPECTACLE_MUSICAL-BURLESQUE"},
                            {"code": 1112, "label": "Comédie-Ballet", "slug": "SPECTACLE_MUSICAL-COMEDIE_BALLET"},
                            {"code": 1113, "label": "Opéra Comique", "slug": "SPECTACLE_MUSICAL-OPERA_COMIQUE"},
                            {"code": 1114, "label": "Opéra-Ballet", "slug": "SPECTACLE_MUSICAL-OPERA_BALLET"},
                            {"code": 1115, "label": "Théâtre musical", "slug": "SPECTACLE_MUSICAL-THEATRE_MUSICAL"},
                            {"code": -1, "label": "Autre", "slug": "SPECTACLE_MUSICAL-OTHER"},
                        ],
                        "code": 1100,
                        "label": "Spectacle Musical / Cabaret / Opérette",
                    },
                    {
                        "children": [
                            {"code": 1201, "label": "Conte", "slug": "SPECTACLE_JEUNESSE-CONTE"},
                            {"code": 1202, "label": "Théâtre jeunesse", "slug": "SPECTACLE_JEUNESSE-THEATRE_JEUNESSE"},
                            {
                                "code": 1203,
                                "label": "Spectacle Petite Enfance",
                                "slug": "SPECTACLE_JEUNESSE-SPECTACLE_PETITE_ENFANCE",
                            },
                            {"code": 1204, "label": "Magie Enfance", "slug": "SPECTACLE_JEUNESSE-MAGIE_ENFANCE"},
                            {
                                "code": 1205,
                                "label": "Spectacle pédagogique",
                                "slug": "SPECTACLE_JEUNESSE-SPECTACLE_PEDAGOGIQUE",
                            },
                            {"code": 1206, "label": "Marionettes", "slug": "SPECTACLE_JEUNESSE-MARIONETTES"},
                            {
                                "code": 1207,
                                "label": "Comédie musicale jeunesse",
                                "slug": "SPECTACLE_JEUNESSE-COMEDIE_MUSICALE_JEUNESSE",
                            },
                            {"code": 1208, "label": "Théâtre d'Ombres", "slug": "SPECTACLE_JEUNESSE-THEATRE_D_OMBRES"},
                            {"code": -1, "label": "Autre", "slug": "SPECTACLE_JEUNESSE-OTHER"},
                        ],
                        "code": 1200,
                        "label": "Spectacle Jeunesse",
                    },
                    {
                        "children": [
                            {"code": 1301, "label": "Boulevard", "slug": "THEATRE-BOULEVARD"},
                            {"code": 1302, "label": "Classique", "slug": "THEATRE-CLASSIQUE"},
                            {"code": 1303, "label": "Comédie", "slug": "THEATRE-COMEDIE"},
                            {"code": 1304, "label": "Contemporain", "slug": "THEATRE-CONTEMPORAIN"},
                            {"code": 1305, "label": "Lecture", "slug": "THEATRE-LECTURE"},
                            {
                                "code": 1306,
                                "label": "Spectacle Scénographique",
                                "slug": "THEATRE-SPECTACLE_SCENOGRAPHIQUE",
                            },
                            {"code": 1307, "label": "Théâtre Experimental", "slug": "THEATRE-THEATRE_EXPERIMENTAL"},
                            {"code": 1308, "label": "Théâtre d'Objet", "slug": "THEATRE-THEATRE_D_OBJET"},
                            {"code": 1309, "label": "Tragédie", "slug": "THEATRE-TRAGEDIE"},
                            {"code": -1, "label": "Autre", "slug": "THEATRE-OTHER"},
                        ],
                        "code": 1300,
                        "label": "Théâtre",
                    },
                    {
                        "children": [
                            {"code": 1401, "label": "Performance", "slug": "PLURIDISCIPLINAIRE-PERFORMANCE"},
                            {"code": 1402, "label": "Poésie", "slug": "PLURIDISCIPLINAIRE-POESIE"},
                            {"code": -1, "label": "Autre", "slug": "PLURIDISCIPLINAIRE-OTHER"},
                        ],
                        "code": 1400,
                        "label": "Pluridisciplinaire",
                    },
                    {
                        "children": [
                            {"code": 1501, "label": "Son et lumière", "slug": "OTHER-SON_ET_LUMIERE"},
                            {"code": 1502, "label": "Spectacle sur glace", "slug": "OTHER-SPECTACLE_SUR_GLACE"},
                            {"code": 1503, "label": "Spectacle historique", "slug": "OTHER-SPECTACLE_HISTORIQUE"},
                            {"code": 1504, "label": "Spectacle aquatique", "slug": "OTHER-SPECTACLE_AQUATIQUE"},
                            {"code": -1, "label": "Autre", "slug": "OTHER-OTHER"},
                        ],
                        "code": 1500,
                        "label": "Autre (spectacle sur glace, historique, aquatique, …)  ",
                    },
                    {
                        "children": [
                            {"code": 1511, "label": "Opéra série", "slug": "OPERA-OPERA_SERIE"},
                            {"code": 1512, "label": "Grand opéra", "slug": "OPERA-GRAND_OPERA"},
                            {"code": 1513, "label": "Opéra bouffe", "slug": "OPERA-OPERA_BOUFFE"},
                            {"code": 1514, "label": "Opéra comique", "slug": "OPERA-OPERA_COMIQUE"},
                            {"code": 1515, "label": "Opéra-ballet", "slug": "OPERA-OPERA_BALLET"},
                            {"code": 1516, "label": "Singspiel", "slug": "OPERA-SINGSPIEL"},
                            {"code": -1, "label": "Autre", "slug": "OPERA-OTHER"},
                        ],
                        "code": 1510,
                        "label": "Opéra",
                    },
                    {"children": [{"code": -1, "label": "Autre", "slug": "OTHER"}], "code": -1, "label": "Autre"},
                ],
            },
            {
                "name": "MOVIE",
                "values": [
                    {"name": "ACTION", "value": "Action"},
                    {"name": "ANIMATION", "value": "Animation"},
                    {"name": "MARTIAL_ARTS", "value": "Arts martiaux"},
                    {"name": "ADVENTURE", "value": "Aventure"},
                    {"name": "BIOPIC", "value": "Biopic"},
                    {"name": "BOLLYWOOD", "value": "Bollywood"},
                    {"name": "COMEDY", "value": "Comédie"},
                    {"name": "COMEDY_DRAMA", "value": "Comédie dramatique"},
                    {"name": "MUSICAL", "value": "Comédie musicale"},
                    {"name": "CONCERT", "value": "Concert"},
                    {"name": "DIVERS", "value": "Divers"},
                    {"name": "DOCUMENTARY", "value": "Documentaire"},
                    {"name": "DRAMA", "value": "Drame"},
                    {"name": "KOREAN_DRAMA", "value": "Drame coréen"},
                    {"name": "SPY", "value": "Espionnage"},
                    {"name": "EXPERIMENTAL", "value": "Expérimental"},
                    {"name": "FAMILY", "value": "Familial"},
                    {"name": "FANTASY", "value": "Fantastique"},
                    {"name": "WARMOVIE", "value": "Guerre"},
                    {"name": "HISTORICAL", "value": "Historique"},
                    {"name": "HISTORICAL_EPIC", "value": "Historique-épique"},
                    {"name": "HORROR", "value": "Horreur"},
                    {"name": "JUDICIAL", "value": "Judiciaire"},
                    {"name": "MUSIC", "value": "Musique"},
                    {"name": "OPERA", "value": "Opéra"},
                    {"name": "PERFORMANCE", "value": "Performance"},
                    {"name": "DETECTIVE", "value": "Policier"},
                    {"name": "ROMANCE", "value": "Romance"},
                    {"name": "SCIENCE_FICTION", "value": "Science-fiction"},
                    {"name": "SPORT_EVENT", "value": "Sport"},
                    {"name": "THRILLER", "value": "Thriller"},
                    {"name": "WESTERN", "value": "Western"},
                    {"name": "EROTIC", "value": "Érotique"},
                ],
                "trees": [
                    {"label": "Action", "name": "ACTION"},
                    {"label": "Aventure", "name": "ADVENTURE"},
                    {"label": "Animation", "name": "ANIMATION"},
                    {"label": "Biopic", "name": "BIOPIC"},
                    {"label": "Bollywood", "name": "BOLLYWOOD"},
                    {"label": "Comédie", "name": "COMEDY"},
                    {"label": "Comédie dramatique", "name": "COMEDY_DRAMA"},
                    {"label": "Concert", "name": "CONCERT"},
                    {"label": "Policier", "name": "DETECTIVE"},
                    {"label": "Divers", "name": "DIVERS"},
                    {"label": "Documentaire", "name": "DOCUMENTARY"},
                    {"label": "Drame", "name": "DRAMA"},
                    {"label": "Érotique", "name": "EROTIC"},
                    {"label": "Expérimental", "name": "EXPERIMENTAL"},
                    {"label": "Familial", "name": "FAMILY"},
                    {"label": "Fantastique", "name": "FANTASY"},
                    {"label": "Historique", "name": "HISTORICAL"},
                    {"label": "Historique-épique", "name": "HISTORICAL_EPIC"},
                    {"label": "Horreur", "name": "HORROR"},
                    {"label": "Judiciaire", "name": "JUDICIAL"},
                    {"label": "Drame coréen", "name": "KOREAN_DRAMA"},
                    {"label": "Arts martiaux", "name": "MARTIAL_ARTS"},
                    {"label": "Musique", "name": "MUSIC"},
                    {"label": "Comédie musicale", "name": "MUSICAL"},
                    {"label": "Opéra", "name": "OPERA"},
                    {"label": "Performance", "name": "PERFORMANCE"},
                    {"label": "Romance", "name": "ROMANCE"},
                    {"label": "Science-fiction", "name": "SCIENCE_FICTION"},
                    {"label": "Sport", "name": "SPORT_EVENT"},
                    {"label": "Espionnage", "name": "SPY"},
                    {"label": "Thriller", "name": "THRILLER"},
                    {"label": "Guerre", "name": "WARMOVIE"},
                    {"label": "Western", "name": "WESTERN"},
                ],
            },
        ]


class CategoriesTest:
    def test_returns_200(self, client):
        response = client.get("/native/v1/categories")

        assert response.status_code == 200


class OfferChroniclesTest:
    def test_get_offer_chronicles(self, client):
        product = offers_factories.ProductFactory(name="Test Product")
        offer = offers_factories.OfferFactory(product=product)
        chronicles_factories.ChronicleFactory(
            products=[product],
            content="Test Chronicle",
            isActive=True,
            isSocialMediaDiffusible=True,
        )
        chronicles_factories.ChronicleFactory(
            products=[product], content="Test Chronicle 2", isActive=True, isSocialMediaDiffusible=True
        )

        offer_id = offer.id
        nb_queries = 1  # select offer
        nb_queries += 1  # select chronicles
        with assert_num_queries(nb_queries):
            response = client.get(f"/native/v1/offer/{offer_id}/chronicles")
        assert response.status_code == 200

        contents = [chronicle["content"] for chronicle in response.json["chronicles"]]
        assert "Test Chronicle 2" in contents
        assert "Test Chronicle" in contents

    def test_get_offer_chronicles_with_no_author(self, client):
        product = offers_factories.ProductFactory(name="Test Product")
        offer = offers_factories.OfferFactory(product=product)
        chronicles_factories.ChronicleFactory(
            products=[product],
            content="Test Chronicle",
            isActive=True,
            isSocialMediaDiffusible=True,
            firstName="Book club user",
            isIdentityDiffusible=True,
            age=18,
            city="Paris",
        )

        offer_id = offer.id
        nb_queries = 1  # select offer
        nb_queries += 1  # select chronicles
        with assert_num_queries(nb_queries):
            response = client.get(f"/native/v1/offer/{offer_id}/chronicles")
        assert response.status_code == 200

        author = response.json["chronicles"][0]["author"]
        assert author["firstName"] == "Book club user"
        assert author["age"] == 18
        assert author["city"] == "Paris"

    def test_get_offer_chronicles_without_product(self, client):
        offer = offers_factories.OfferFactory()
        chronicles_factories.ChronicleFactory(
            offers=[offer], content="Test Chronicle", isActive=True, isSocialMediaDiffusible=True
        )
        chronicles_factories.ChronicleFactory(
            offers=[offer], content="Test Chronicle 2", isActive=True, isSocialMediaDiffusible=True
        )

        offer_id = offer.id
        nb_queries = 1  # select offer
        nb_queries += 1  # select chronicles
        with assert_num_queries(nb_queries):
            response = client.get(f"/native/v1/offer/{offer_id}/chronicles")

        assert response.status_code == 200
        contents = [chronicle["content"] for chronicle in response.json["chronicles"]]
        assert "Test Chronicle 2" in contents
        assert "Test Chronicle" in contents

    def test_get_offer_chronicles_with_no_chronicles(self, client):
        offer = offers_factories.OfferFactory()
        offer_id = offer.id
        nb_queries = 1  # select offer
        nb_queries += 1  # select chronicles
        with assert_num_queries(nb_queries):
            response = client.get(f"/native/v1/offer/{offer_id}/chronicles")
        assert response.status_code == 200
        assert response.json["chronicles"] == []

    def test_get_offer_chronicles_returns_full_content(self, client):
        product = offers_factories.ProductFactory()
        offer = offers_factories.OfferFactory(product=product)

        long_text = """
        Vesper is a world built on the ruins of older ones: in the dark of that colossal cavern no one has ever known the edges of, empires rise and fall like flickering candles.

        Civilization huddles around pits of the light that falls through the cracks in firmament, known by men as the Glare. 
        It is the unblinking stare of the never-setting sun that destroyed the Old World, the cruel mortar that allows survival far below. 
        Few venture beyond its cast, for in the monstrous and primordial darkness of the Gloam old gods and devils prowl as men made into darklings worship hateful powers. 
        So it has been for millennia, from the fabled reign of the Antediluvians to these modern nights of blackpowder and sail. And now the times are changing again.

        The fragile peace that emerged after the last of the Succession Wars is falling apart, the great powers squabbling over trade and colonies. 
        Conspiracies bloom behind every throne, gods of the Old Night offer wicked pacts to those who would tear down the order things and of all Vesper only the Watch has seen the signs of the madness to come. 
        God-killers whose duty is to enforce the peace between men and monsters, the Watch would hunt the shadows. 
        Yet its captain-generals know the strength of their companies has waned, and to meet the coming doom measures will have to be taken.

        It will begin with Scholomance, the ancient school of the order opened again for the first time in over a century, and the students who will walk its halls."""

        chronicles_factories.ChronicleFactory(
            products=[product], content=long_text, isActive=True, isSocialMediaDiffusible=True
        )

        offer_id = offer.id
        nb_queries = 1  # select offer
        nb_queries += 1  # select chronicles
        with assert_num_queries(nb_queries):
            response = client.get(f"/native/v1/offer/{offer_id}/chronicles")

        assert response.status_code == 200
        assert response.json["chronicles"][0]["content"] == long_text

    def test_get_chronicles_does_not_return_unpublished_chronicles(self, client):
        product = offers_factories.ProductFactory()
        offer = offers_factories.OfferFactory(product=product)
        chronicles_factories.ChronicleFactory(products=[product], isActive=False, isSocialMediaDiffusible=True)
        chronicles_factories.ChronicleFactory(products=[product], isActive=True, isSocialMediaDiffusible=False)

        offer_id = offer.id
        nb_queries = 1  # select offer
        nb_queries += 1  # select chronicles
        with assert_num_queries(nb_queries):
            response = client.get(f"/native/v1/offer/{offer_id}/chronicles")

        assert response.status_code == 200
        assert response.json["chronicles"] == []

    def test_get_chronicles_with_anonymous_user(self, client):
        product = offers_factories.ProductFactory()
        offer = offers_factories.OfferFactory(product=product)
        chronicles_factories.ChronicleFactory(
            products=[product],
            isActive=True,
            isSocialMediaDiffusible=True,
            isIdentityDiffusible=False,
            firstName="Anonymous",
        )

        offer_id = offer.id
        nb_queries = 1  # select offer
        nb_queries += 1  # select chronicles
        with assert_num_queries(nb_queries):
            response = client.get(f"/native/v1/offer/{offer_id}/chronicles")

        assert response.status_code == 200
        assert response.json["chronicles"][0]["author"] is None

    def test_chronicles_are_ordered_by_id(self, client):
        product = offers_factories.ProductFactory()
        offer = offers_factories.OfferFactory(product=product)
        chronicles_factories.ChronicleFactory(id=7777, products=[product], isActive=True, isSocialMediaDiffusible=True)
        chronicles_factories.ChronicleFactory(id=8888, products=[product], isActive=True, isSocialMediaDiffusible=True)

        offer_id = offer.id
        nb_queries = 1  # select offer
        nb_queries += 1  # select chronicles
        with assert_num_queries(nb_queries):
            response = client.get(f"/native/v1/offer/{offer_id}/chronicles")

        assert response.status_code == 200
        chronicles = response.json["chronicles"]

        assert chronicles[0]["id"] == 8888
        assert chronicles[1]["id"] == 7777
