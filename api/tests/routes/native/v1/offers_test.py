from datetime import datetime
from datetime import timedelta
from unittest import mock
from unittest.mock import patch

import pytest
import time_machine

import pcapi.core.artist.factories as artists_factories
import pcapi.core.chronicles.factories as chronicles_factories
import pcapi.core.mails.testing as mails_testing
import pcapi.core.offers.factories as offers_factories
import pcapi.core.providers.factories as providers_factories
import pcapi.local_providers.cinema_providers.constants as cinema_providers_constants
import pcapi.notifications.push.testing as notifications_testing
from pcapi import settings
from pcapi.core.artist.models import ArtistType
from pcapi.core.bookings.factories import BookingFactory
from pcapi.core.categories import subcategories
from pcapi.core.geography.factories import AddressFactory
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offerers.factories import OffererAddressFactory
from pcapi.core.offerers.factories import VenueFactory
from pcapi.core.offers.models import ImageType
from pcapi.core.offers.models import Offer
from pcapi.core.providers.constants import BookFormat
from pcapi.core.providers.repository import get_provider_by_local_class
from pcapi.core.reactions.factories import ReactionFactory
from pcapi.core.reactions.models import ReactionTypeEnum
from pcapi.core.testing import assert_no_duplicated_queries
from pcapi.core.testing import assert_num_queries
from pcapi.core.users import factories as users_factories
from pcapi.core.users.factories import UserFactory
from pcapi.models import db
from pcapi.models.offer_mixin import OfferValidationStatus
from pcapi.routes.native.v1.serialization.offers import MAX_PREVIEW_CHRONICLES
from pcapi.utils import date as date_utils

from tests.connectors.cgr import soap_definitions
from tests.local_providers.cinema_providers.boost import fixtures as boost_fixtures
from tests.local_providers.cinema_providers.cgr import fixtures as cgr_fixtures


pytestmark = pytest.mark.usefixtures("db_session")


class OffersTest:
    @time_machine.travel("2020-01-01", tick=False)
    def test_get_event_offer(self, client):
        ean = "1234567899999"
        extra_data = {
            "allocineId": 12345,
            "author": "mandibule",
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
            ean=ean,
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
        with assert_num_queries(nb_queries):
            with assert_no_duplicated_queries():
                response = client.get(f"/native/v1/offer/{offer_id}")
                assert response.status_code == 200

        offer = db.session.get(Offer, offer.id)
        assert offer.ean == ean
        assert "ean" not in offer.extraData
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
            "ean": "1234567899999",
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
            "address": offer.venue.offererAddress.address.street,
            "city": offer.venue.offererAddress.address.city,
            "coordinates": {
                "latitude": float(offer.venue.offererAddress.address.latitude),
                "longitude": float(offer.venue.offererAddress.address.longitude),
            },
            "name": "il est venu le temps des names",
            "offerer": {"name": offer.venue.managingOfferer.name},
            "postalCode": offer.venue.offererAddress.address.postalCode,
            "publicName": "il est venu le temps des names",
            "isPermanent": False,
            "isOpenToPublic": False,
            "timezone": offer.venue.offererAddress.address.timezone,
            "bannerUrl": offer.venue.bannerUrl,
        }
        assert response.json["withdrawalDetails"] == "modalité de retrait"
        assert response.json["publicationDate"] == None
        assert response.json["bookingAllowedDatetime"] == None

    def test_get_offer_with_unlimited_stock(self, client):
        product = offers_factories.ProductFactory(thumbCount=1)
        offer = offers_factories.OfferFactory(product=product, venue__isPermanent=True)
        offers_factories.ThingStockFactory(offer=offer, price=12.34, quantity=None)

        offer_id = offer.id
        # 1. select offer
        # 2. select stocks
        # 3. select mediations
        # 4. select chronicles
        # 5. select artists
        with assert_num_queries(5):
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
        # 2. select product with artists
        # 3. select stocks
        # 4. select mediations
        # 5. check cinema venue_provider exists
        # 6. check offer is from current cinema provider
        # 7. select active cinema provider
        # 8. update offer
        # 9. select chronicles
        # 10. selecte features
        # 11. reload offer
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
        with assert_num_queries(nb_query):
            response = client.get(f"/native/v1/offer/{offer_id}")

        assert response.status_code == 200
        assert len(response.json["stocks"]) == 1
        assert len(offer.stocks) == 2

    def test_get_offer_with_product_mediation_and_thumb(self, client):
        product = offers_factories.ProductFactory(thumbCount=1, subcategoryId=subcategories.LIVRE_PAPIER.id)
        uuid = "1"
        product_mediation = offers_factories.ProductMediationFactory(
            product=product, uuid=uuid, imageType=ImageType.RECTO
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
        # 5. select products and artists
        with assert_num_queries(5):
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
            product=product, uuid=uuid, imageType=ImageType.RECTO
        )
        offers_factories.ProductMediationFactory(product=product, imageType=ImageType.VERSO)
        offer = offers_factories.OfferFactory(
            product=product, venue__isPermanent=True, subcategoryId=subcategories.LIVRE_PAPIER.id
        )
        offers_factories.ThingStockFactory(offer=offer, price=12.34)

        offer_id = offer.id
        # 1. select offer
        # 2. select stocks
        # 3. select mediations
        # 4. select chronicles
        # 5. select artists
        with assert_num_queries(5):
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
        # 5. select artists
        with assert_num_queries(5):
            response = client.get(f"/native/v1/offer/{offer_id}")

        assert response.status_code == 200
        assert response.json["image"] == {
            "url": "http://localhost/storage/thumbs/products/N4",
            "credit": None,
        }

    def test_get_offer_with_mediation_and_product_mediation(self, client):
        product = offers_factories.ProductFactory(thumbCount=1, subcategoryId=subcategories.LIVRE_PAPIER.id)
        offers_factories.ProductMediationFactory(product=product, imageType=ImageType.RECTO)
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
        # 5. select artists
        with assert_num_queries(5):
            response = client.get(f"/native/v1/offer/{offer_id}")

        assert response.status_code == 200
        assert response.json["image"] == {
            "url": "http://localhost/storage/thumbs/mediations/N4_1",
            "credit": "street credit",
        }


class OffersV2Test:
    base_num_queries = 1  # select offer with joins
    base_num_queries += 1  # select mediations (selectinload)
    base_num_queries += 1  # select stocks (selectinload)
    base_num_queries += 1  # select chronicles (selectinload)

    num_queries_with_product = 1  # select artists (selectinload)

    num_queries_for_cinema = 1  # select EXISTS venue_provider
    num_queries_for_cinema += 1  # select EXISTS provider
    # num_queries_for_cinema += 1  # select products with artists (selectinload)

    num_queries_for_stock_sync = 1  # update stock
    num_queries_for_stock_sync += 1  # select cinema_provider_pivot

    @time_machine.travel("2020-01-01", tick=False)
    def test_get_event_offer(self, client):
        extra_data = {
            "allocineId": 12345,
            "author": "mandibule",
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
            ean="1234567899999",
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
            "ean": "1234567899999",
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
            "address": offer.venue.offererAddress.address.street,
            "city": offer.venue.offererAddress.address.city,
            "coordinates": {
                "latitude": float(offer.venue.offererAddress.address.latitude),
                "longitude": float(offer.venue.offererAddress.address.longitude),
            },
            "name": "il est venu le temps des names",
            "offerer": {"name": offer.venue.managingOfferer.name},
            "postalCode": offer.venue.offererAddress.address.postalCode,
            "publicName": "il est venu le temps des names",
            "isPermanent": False,
            "isOpenToPublic": False,
            "timezone": offer.venue.offererAddress.address.timezone,
            "bannerUrl": offer.venue.bannerUrl,
        }
        assert response.json["withdrawalDetails"] == "modalité de retrait"
        assert response.json["publicationDate"] == None
        assert response.json["bookingAllowedDatetime"] == None

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

        num_queries = self.base_num_queries + self.num_queries_for_cinema
        num_queries += 1  # select products with artists (selectinload)
        num_queries += 1  # select cinema_provider_pivot
        num_queries += 1  # update offer
        num_queries += 1  # select feature
        num_queries += 1  # reload offer
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
        offers_factories.ProductMediationFactory(product=product, uuid=uuid, imageType=ImageType.RECTO)
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
        offers_factories.ProductMediationFactory(product=product, uuid=first_uuid, imageType=ImageType.RECTO)
        offers_factories.ProductMediationFactory(product=product, uuid=second_uuid, imageType=ImageType.VERSO)
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
        offers_factories.ProductMediationFactory(product=product, imageType=ImageType.RECTO)
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
            "coordinates": {"latitude": float(address.latitude), "longitude": float(address.longitude)},
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
        assert response.json["extraData"]["bookFormat"] == "Poche"

    def test_offer_extra_data_book_format(self, client):
        extra_data = {"bookFormat": BookFormat.MOYEN_FORMAT}
        offer = offers_factories.OfferFactory(extraData=extra_data)

        offer_id = offer.id
        with assert_num_queries(self.base_num_queries):
            response = client.get(f"/native/v2/offer/{offer_id}")
        assert response.status_code == 200
        assert response.json["extraData"]["bookFormat"] == "Moyen format"

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
        booking_allowed_datetime = datetime(2050, 1, 1)
        offer = offers_factories.OfferFactory(bookingAllowedDatetime=booking_allowed_datetime)

        offer_id = offer.id
        with assert_num_queries(self.base_num_queries):
            response = client.get(f"/native/v2/offer/{offer_id}")

        assert response.status_code == 200
        assert response.json["publicationDate"] == "2050-01-01T00:00:00Z"
        assert response.json["bookingAllowedDatetime"] == "2050-01-01T00:00:00Z"

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

    def test_get_headline_offer(self, client):
        offer = offers_factories.OfferFactory()
        offer_id = offer.id
        with assert_num_queries(self.base_num_queries):
            response = client.get(f"/native/v2/offer/{offer_id}")

        assert response.status_code == 200
        assert response.json["isHeadline"] is False

    def test_get_not_headline_offer(self, client):
        headline_offer = offers_factories.HeadlineOfferFactory()
        offer_id = headline_offer.offer.id
        with assert_num_queries(self.base_num_queries + 1):  # FF WIP_REFACTO_FUTURE_OFFER
            response = client.get(f"/native/v2/offer/{offer_id}")

        assert response.status_code == 200
        assert response.json["isHeadline"] is True

    def test_return_venue_public_name(self, client):
        venue = VenueFactory(name="Legal name", publicName="Public name")
        offer_id = offers_factories.OfferFactory(venue=venue).id

        response = client.get(f"/native/v2/offer/{offer_id}")

        assert response.status_code == 200
        assert response.json["venue"]["name"] == "Public name"


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
        ean = "1234567899999"
        extra_data = {
            "allocineId": 12345,
            "author": "mandibule",
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
            ean=ean,
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
            "ean": "1234567899999",
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
            "address": offer.venue.offererAddress.address.street,
            "city": offer.venue.offererAddress.address.city,
            "coordinates": {
                "latitude": float(offer.venue.offererAddress.address.latitude),
                "longitude": float(offer.venue.offererAddress.address.longitude),
            },
            "name": offer.venue.name,
            "offerer": {"name": offer.venue.managingOfferer.name},
            "postalCode": offer.venue.offererAddress.address.postalCode,
            "publicName": offer.venue.publicName,
            "isPermanent": False,
            "isOpenToPublic": False,
            "timezone": offer.venue.offererAddress.address.timezone,
            "bannerUrl": offer.venue.bannerUrl,
        }
        assert response_offer["withdrawalDetails"] is None

        assert response_offer["publicationDate"] == None
        assert response_offer["bookingAllowedDatetime"] == None


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


class OfferChroniclesTest:
    # select offer
    # select chronicles
    expected_num_queries = 2

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
        db.session.expire_all()
        with assert_num_queries(self.expected_num_queries):
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
        db.session.expire_all()
        with assert_num_queries(self.expected_num_queries):
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
        db.session.expire_all()
        with assert_num_queries(self.expected_num_queries):
            response = client.get(f"/native/v1/offer/{offer_id}/chronicles")

        assert response.status_code == 200
        contents = [chronicle["content"] for chronicle in response.json["chronicles"]]
        assert "Test Chronicle 2" in contents
        assert "Test Chronicle" in contents

    def test_get_offer_chronicles_with_no_chronicles(self, client):
        offer = offers_factories.OfferFactory()
        offer_id = offer.id
        db.session.expire_all()
        with assert_num_queries(self.expected_num_queries):
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
        db.session.expire_all()
        with assert_num_queries(self.expected_num_queries):
            response = client.get(f"/native/v1/offer/{offer_id}/chronicles")

        assert response.status_code == 200
        assert response.json["chronicles"][0]["content"] == long_text

    def test_get_chronicles_does_not_return_unpublished_chronicles(self, client):
        product = offers_factories.ProductFactory()
        offer = offers_factories.OfferFactory(product=product)
        chronicles_factories.ChronicleFactory(products=[product], isActive=False, isSocialMediaDiffusible=True)
        chronicles_factories.ChronicleFactory(products=[product], isActive=True, isSocialMediaDiffusible=False)

        offer_id = offer.id
        db.session.expire_all()
        with assert_num_queries(self.expected_num_queries):
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
        db.session.expire_all()
        with assert_num_queries(self.expected_num_queries):
            response = client.get(f"/native/v1/offer/{offer_id}/chronicles")

        assert response.status_code == 200
        assert response.json["chronicles"][0]["author"] is None

    def test_chronicles_are_ordered_by_id(self, client):
        product = offers_factories.ProductFactory()
        offer = offers_factories.OfferFactory(product=product)
        chronicles_factories.ChronicleFactory(id=7777, products=[product], isActive=True, isSocialMediaDiffusible=True)
        chronicles_factories.ChronicleFactory(id=8888, products=[product], isActive=True, isSocialMediaDiffusible=True)

        offer_id = offer.id
        db.session.expire_all()
        with assert_num_queries(self.expected_num_queries):
            response = client.get(f"/native/v1/offer/{offer_id}/chronicles")

        assert response.status_code == 200
        chronicles = response.json["chronicles"]

        assert chronicles[0]["id"] == 8888
        assert chronicles[1]["id"] == 7777
