import logging
from datetime import date
from datetime import datetime
from datetime import time
from datetime import timedelta

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


pytestmark = pytest.mark.usefixtures("db_session")


class OffersTest:
    nb_queries = 1  # select offer
    nb_queries += 1  # select stocks
    nb_queries += 1  # select opening hours
    nb_queries += 1  # select mediations
    nb_queries += 1  # select chronicles

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
        offer = offers_factories.EventOfferFactory(
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
        offerers_factories.OpeningHoursFactory(offer=offer, venue=None)

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
            beginningDatetime=date_utils.get_naive_utc_now() - timedelta(days=1),
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

        with assert_num_queries(self.nb_queries):
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
        assert response.json["openingHours"] == {
            "MONDAY": [["10:00", "13:00"], ["14:00", "19:30"]],
            "TUESDAY": None,
            "WEDNESDAY": None,
            "THURSDAY": None,
            "FRIDAY": None,
            "SATURDAY": None,
            "SUNDAY": None,
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
        assert response.json["isEvent"] is True

    def test_get_offer_with_unlimited_stock(self, client):
        product = offers_factories.ProductFactory(thumbCount=1)
        offer = offers_factories.OfferFactory(product=product, venue__isPermanent=True)
        offers_factories.ThingStockFactory(offer=offer, price=12.34, quantity=None)

        offer_id = offer.id
        with assert_num_queries(self.nb_queries + 1):  # select artists
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
        with assert_num_queries(self.nb_queries):
            with assert_no_duplicated_queries():
                response = client.get(f"/native/v1/offer/{offer_id}")
                assert response.status_code == 200

    def test_get_thing_offer(self, client):
        offer = offers_factories.OfferFactory(venue__isPermanent=True, subcategoryId=subcategories.CARTE_MUSEE.id)
        offers_factories.ThingStockFactory(offer=offer, price=12.34)

        offer_id = offer.id
        with assert_num_queries(self.nb_queries):
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
        assert response.json["isEvent"] is False

    def test_get_digital_offer_with_available_activation_and_no_expiration_date(self, client):
        stock = offers_factories.StockWithActivationCodesFactory()
        offer_id = stock.offer.id

        with assert_num_queries(self.nb_queries + 1):  # select activation_code
            with assert_no_duplicated_queries():
                response = client.get(f"/native/v1/offer/{offer_id}")
                assert response.status_code == 200

        assert response.json["stocks"][0]["activationCode"] == {"expirationDate": None}

    def test_get_digital_offer_with_available_activation_code_and_expiration_date(self, client):
        stock = offers_factories.StockWithActivationCodesFactory(activationCodes__expirationDate=datetime(2050, 1, 1))
        offer_id = stock.offer.id

        with assert_num_queries(self.nb_queries + 1):  # select activation_code
            with assert_no_duplicated_queries():
                response = client.get(f"/native/v1/offer/{offer_id}")
                assert response.status_code == 200

        assert response.json["stocks"][0]["activationCode"] == {"expirationDate": "2050-01-01T00:00:00Z"}

    def test_get_digital_offer_without_available_activation_code(self, client):
        stock = offers_factories.StockWithActivationCodesFactory(activationCodes__expirationDate=datetime(2000, 1, 1))
        offer_id = stock.offer.id

        with assert_num_queries(self.nb_queries + 1):  # activation_code
            with assert_no_duplicated_queries():
                response = client.get(f"/native/v1/offer/{offer_id}")
                assert response.status_code == 200

        assert response.json["stocks"][0]["activationCode"] is None

    @time_machine.travel("2020-01-01")
    def test_get_expired_offer(self, client):
        stock = offers_factories.EventStockFactory(beginningDatetime=date_utils.get_naive_utc_now() - timedelta(days=1))

        offer_id = stock.offer.id

        with assert_num_queries(self.nb_queries):
            with assert_no_duplicated_queries():
                response = client.get(f"/native/v1/offer/{offer_id}")

        assert response.json["isExpired"]

    def test_get_offer_not_found(self, client):
        # select offer
        # rollback
        # rollback
        with assert_num_queries(3):
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
        # rollback
        with assert_num_queries(3):
            response = client.get(f"/native/v1/offer/{offer_id}")
            assert response.status_code == 404

    def should_have_metadata_describing_the_offer(self, client):
        offer = offers_factories.ThingOfferFactory()

        offer_id = offer.id
        with assert_num_queries(self.nb_queries):
            response = client.get(f"/native/v1/offer/{offer_id}")
            assert response.status_code == 200

        assert isinstance(response.json["metadata"], dict)
        assert response.json["metadata"]["@type"] == "Product"

    def should_not_return_soft_deleted_offer(self, client):
        offer = offers_factories.OfferFactory()
        offers_factories.StockFactory(offer=offer, quantity=1, isSoftDeleted=True)
        non_deleted_stock = offers_factories.StockFactory(offer=offer, quantity=1)

        offer_id = offer.id
        with assert_num_queries(self.nb_queries):
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
        with assert_num_queries(self.nb_queries):
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
        with assert_num_queries(self.nb_queries + 1):  # products and artists
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
        with assert_num_queries(self.nb_queries + 1):  # select artists
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
        with assert_num_queries(self.nb_queries + 1):  # select artists
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
        with assert_num_queries(self.nb_queries + 1):  # select artists
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
    base_num_queries += 1  # select opening hours (selectinload)
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
            beginningDatetime=date_utils.get_naive_utc_now() - timedelta(days=1),
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
        assert response.json["isEvent"] is True

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
        assert response.json["isEvent"] is False

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
        stock = offers_factories.EventStockFactory(beginningDatetime=date_utils.get_naive_utc_now() - timedelta(days=1))

        offer_id = stock.offer.id
        with assert_num_queries(self.base_num_queries):
            response = client.get(f"/native/v2/offer/{offer_id}")

        assert response.json["isExpired"]

    def test_get_offer_not_found(self, client):
        # 1. select offer
        # 2. rollback
        # 3. rollback
        with assert_num_queries(3):
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
        # 3. rollback
        with assert_num_queries(3):
            response = client.get(f"/native/v2/offer/{offer_id}")
            assert response.status_code == 404

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
        with assert_num_queries(num_queries):
            response = client.get(f"/native/v2/offer/{offer_id}")

        assert response.status_code == 200
        assert response.json["isExternalBookingsDisabled"] is booking_disabled

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
        chronicles_factories.ChronicleFactory(
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
        artist_3 = artists_factories.ArtistFactory(is_blacklisted=True)
        artists_factories.ArtistProductLinkFactory(artist_id=artist_1.id, product_id=product.id)
        artists_factories.ArtistProductLinkFactory(artist_id=artist_2.id, product_id=product.id)
        artists_factories.ArtistProductLinkFactory(artist_id=artist_3.id, product_id=product.id)

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

        with assert_num_queries(self.base_num_queries):
            response = client.get(f"/native/v2/offer/{offer_id}")

        assert response.status_code == 200
        assert response.json["isHeadline"] is True

    def test_return_venue_public_name(self, client):
        venue = VenueFactory(name="Legal name", publicName="Public name")
        offer_id = offers_factories.OfferFactory(venue=venue).id

        response = client.get(f"/native/v2/offer/{offer_id}")

        assert response.status_code == 200
        assert response.json["venue"]["name"] == "Public name"

    def test_get_offer_with_no_chronicles(self, client):
        offer = offers_factories.OfferFactory()

        offer_id = offer.id
        response = client.get(f"/native/v2/offer/{offer_id}")

        assert response.status_code == 200
        assert response.json["chroniclesCount"] == 0

    def test_get_offer_with_chronicles(self, client):
        offer = offers_factories.OfferFactory()
        chronicles_factories.ChronicleFactory(offers=[offer], isSocialMediaDiffusible=True)
        chronicles_factories.ChronicleFactory(offers=[offer], isSocialMediaDiffusible=True)

        offer_id = offer.id
        response = client.get(f"/native/v2/offer/{offer_id}")

        assert response.status_code == 200
        assert response.json["chroniclesCount"] == 2

    def test_get_offer_with_product_with_no_chronicles(self, client):
        product = offers_factories.ProductFactory()
        offer = offers_factories.OfferFactory(product=product)

        offer_id = offer.id
        response = client.get(f"/native/v2/offer/{offer_id}")

        assert response.status_code == 200
        assert response.json["chroniclesCount"] == 0

    def test_get_offer_with_product_with_chronicles(self, client):
        product = offers_factories.ProductFactory(chroniclesCount=1)
        offer = offers_factories.OfferFactory(product=product)

        offer_id = offer.id
        response = client.get(f"/native/v2/offer/{offer_id}")

        assert response.status_code == 200
        assert response.json["chroniclesCount"] == 1

    def test_get_offer_with_chronicles_with_product_with_chronicles(self, client):
        product = offers_factories.ProductFactory(chroniclesCount=2)
        offer = offers_factories.OfferFactory(product=product)
        chronicles_factories.ChronicleFactory(offers=[offer], isSocialMediaDiffusible=True)

        offer_id = offer.id
        response = client.get(f"/native/v2/offer/{offer_id}")

        assert response.status_code == 200
        assert response.json["chroniclesCount"] == 2

    def test_get_offer_with_unpublished_chronicles(self, client):
        offer = offers_factories.OfferFactory()
        chronicles_factories.ChronicleFactory(offers=[offer], isActive=False, isSocialMediaDiffusible=False)

        offer_id = offer.id
        response = client.get(f"/native/v2/offer/{offer_id}")

        assert response.status_code == 200
        assert response.json["chroniclesCount"] == 0

    def test_get_offer_with_product_with_unpublished_chronicles(self, client):
        product = offers_factories.ProductFactory()
        offer = offers_factories.OfferFactory(product=product)
        chronicles_factories.ChronicleFactory(products=[product], isActive=False, isSocialMediaDiffusible=False)

        offer_id = offer.id
        response = client.get(f"/native/v2/offer/{offer_id}")

        assert response.status_code == 200
        assert response.json["chroniclesCount"] == 0

    def test_get_offer_with_youtube_video_data(self, client):
        metadata = offers_factories.OfferMetaDataFactory(
            videoUrl="https://www.youtube.com/watch?v=fAkeV1ide0o",
            videoExternalId="fAkeV1ide0o",
            videoTitle="Test Video",
            videoThumbnailUrl="https://example.com/fAkeV1ide0o/thumbnail.jpg",
            videoDuration=123,
        )
        offer_id = metadata.offer.id

        with assert_num_queries(self.base_num_queries):
            response = client.get(f"/native/v2/offer/{offer_id}")

        assert response.status_code == 200
        assert response.json["video"] == {
            "id": "fAkeV1ide0o",
            "title": "Test Video",
            "thumbUrl": "https://example.com/fAkeV1ide0o/thumbnail.jpg",
            "durationSeconds": 123,
        }

    def test_get_offer_with_no_external_id_should_send_error_log(self, client, caplog):
        metadata = offers_factories.OfferMetaDataFactory(
            videoUrl="https://www.youtube.com/watch?v=fAkeV1ide0o",
            videoExternalId=None,
            videoTitle="Test Video",
            videoThumbnailUrl="https://example.com/fAkeV1ide0o/thumbnail.jpg",
            videoDuration=123,
        )
        offer_id = metadata.offer.id

        with caplog.at_level(logging.ERROR):
            response = client.get(f"/native/v2/offer/{offer_id}")
            assert (
                caplog.messages[0]
                == "This offer has a video URL but no videoExternalId in its metaData, and this should not happen"
            )
            assert caplog.records[0].extra == {"offer_id": offer_id}

        assert response.json["video"] is None


class MovieCalendarTest:
    def test_get_movie_shows_with_allocine_id(self, client):
        product = offers_factories.ProductFactory(extraData={"allocineId": 12345})
        address = AddressFactory(latitude=48.85, longitude=2.35)
        stock = offers_factories.EventStockFactory(
            offer__product=product,
            offer__venue__offererAddress__address=address,
            offer__venue__offererAddress__label="Cinéma Parisien",
            beginningDatetime=datetime.now() + timedelta(hours=1),
        )
        today = date.today()
        tomorrow = date.today() + timedelta(days=1)
        params = {
            "allocineId": "12345",
            "latitude": 48.85,
            "longitude": 2.35,
            "from": today,
            "to": tomorrow,
        }
        expected_num_queries = 1  # product
        expected_num_queries += 1  # stocks
        expected_num_queries += 1  # screenings
        with assert_num_queries(expected_num_queries):
            response = client.get("/native/v1/movie/calendar", params=params)
            assert response.status_code == 200

        calendar = response.json["calendar"]
        assert calendar == {
            today.isoformat(): [
                {
                    "address": f"{address.street}, {address.postalCode} {address.city}",
                    "distance": 0.0,
                    "dayScreenings": [
                        {
                            "beginningDatetime": date_utils.format_into_utc_date(stock.beginningDatetime),
                            "features": [],
                            "price": float(stock.price),
                            "stockId": stock.id,
                        }
                    ],
                    "label": stock.offer.offererAddress.label,
                    "nextScreening": {
                        "beginningDatetime": date_utils.format_into_utc_date(stock.beginningDatetime),
                        "features": [],
                        "price": float(stock.price),
                        "stockId": stock.id,
                    },
                    "thumbUrl": None,
                    "venueId": stock.offer.venue.id,
                },
            ],
            tomorrow.isoformat(): [
                {
                    "address": f"{address.street}, {address.postalCode} {address.city}",
                    "distance": 0.0,
                    "dayScreenings": [],
                    "label": stock.offer.offererAddress.label,
                    "nextScreening": {
                        "beginningDatetime": date_utils.format_into_utc_date(stock.beginningDatetime),
                        "features": [],
                        "price": 10.1,
                        "stockId": stock.id,
                    },
                    "thumbUrl": None,
                    "venueId": stock.offer.venue.id,
                },
            ],
        }

    def test_get_movie_shows_with_visa(self, client):
        product = offers_factories.ProductFactory(extraData={"visa": "12345"})
        address = AddressFactory(latitude=48.85, longitude=2.35)
        offers_factories.EventStockFactory(
            offer__product=product,
            offer__venue__offererAddress__address=address,
            beginningDatetime=datetime.now() + timedelta(hours=1),
        )

        today = date.today()
        tomorrow = date.today() + timedelta(days=1)
        params = {
            "visa": "12345",
            "latitude": 48.85,
            "longitude": 2.35,
            "from": today,
            "to": tomorrow,
        }
        expected_num_queries = 1  # product
        expected_num_queries += 1  # stocks
        expected_num_queries += 1  # screenings
        with assert_num_queries(expected_num_queries):
            response = client.get("/native/v1/movie/calendar", params=params)
            assert response.status_code == 200

        assert len(response.json["calendar"][today.isoformat()]) == 1
        assert len(response.json["calendar"][tomorrow.isoformat()]) == 1

    def test_requires_allocine_id_or_visa(self, client):
        params = {
            "latitude": 48.85,
            "longitude": 2.35,
        }
        expected_num_queries = 0  # should fail before fetching anything
        with assert_num_queries(expected_num_queries):
            response = client.get("/native/v1/movie/calendar", params=params)
            assert response.status_code == 400

    def test_cant_have_allocine_id_and_visa(self, client):
        params = {
            "allocineId": "12345",
            "visa": "12345",
            "latitude": 48.85,
            "longitude": 2.35,
        }
        expected_num_queries = 0  # should fail before fetching anything
        with assert_num_queries(expected_num_queries):
            response = client.get("/native/v1/movie/calendar", params=params)
            assert response.status_code == 400

    def test_requires_location(self, client):
        params = {
            "visa": "12345",
            "latitude": 48.85,
        }
        expected_num_queries = 0  # should fail before fetching anything
        with assert_num_queries(expected_num_queries):
            response = client.get("/native/v1/movie/calendar", params=params)
            assert response.status_code == 400

    def test_returns_404_if_product_not_found(self, client):
        params = {
            "allocineId": "12345",
            "latitude": 48.85,
            "longitude": 2.35,
        }
        expected_num_queries = 1  # product
        with assert_num_queries(expected_num_queries):
            response = client.get("/native/v1/movie/calendar", params=params)
            assert response.status_code == 404

    def test_on_no_screenings_found(self, client):
        offers_factories.ProductFactory(extraData={"allocineId": 12345})
        today = date.today()
        tomorrow = date.today() + timedelta(days=1)
        params = {
            "allocineId": "12345",
            "latitude": 48.85,
            "longitude": 2.35,
            "from": today,
            "to": tomorrow,
        }
        expected_num_queries = 1  # product
        expected_num_queries += 1  # stocks
        expected_num_queries += 1  # screenings
        with assert_num_queries(expected_num_queries):
            response = client.get("/native/v1/movie/calendar", params=params)
            assert response.status_code == 200

        assert response.json["calendar"][today.isoformat()] == []
        assert response.json["calendar"][tomorrow.isoformat()] == []

    def test_screenings_are_sorted_by_distance_then_screening_day(self, client):
        product = offers_factories.ProductFactory(extraData={"allocineId": 12345})
        closest_address_for_today = AddressFactory(latitude=48.85, longitude=2.35)
        closest_address_for_tomorrow = AddressFactory(latitude=48.85, longitude=2.35)
        furthest_address_for_today = AddressFactory(latitude=48.84, longitude=2.35)
        furthest_address_for_tomorrow = AddressFactory(latitude=48.84, longitude=2.35)
        today_closest_stock = offers_factories.EventStockFactory(
            offer__product=product,
            offer__venue__offererAddress__address=closest_address_for_today,
            beginningDatetime=datetime.now() + timedelta(hours=1),
        )
        today_furthest_stock = offers_factories.EventStockFactory(
            offer__product=product,
            offer__venue__offererAddress__address=furthest_address_for_today,
            beginningDatetime=datetime.now() + timedelta(hours=1),
        )
        tomorrow_closest_stock = offers_factories.EventStockFactory(
            offer__product=product,
            offer__venue__offererAddress__address=closest_address_for_tomorrow,
            beginningDatetime=datetime.now() + timedelta(hours=23),
        )
        tomorrow_furthest_stock = offers_factories.EventStockFactory(
            offer__product=product,
            offer__venue__offererAddress__address=furthest_address_for_tomorrow,
            beginningDatetime=datetime.now() + timedelta(hours=23),
        )

        today = date.today()
        tomorrow = date.today() + timedelta(days=1)
        params = {
            "allocineId": "12345",
            "latitude": 48.85,
            "longitude": 2.35,
            "from": datetime.combine(today, time.min),
            "to": datetime.combine(tomorrow, time.max),
        }
        expected_num_queries = 1  # product
        expected_num_queries += 1  # stocks
        expected_num_queries += 1  # screenings
        with assert_num_queries(expected_num_queries):
            response = client.get("/native/v1/movie/calendar", params=params)
            assert response.status_code == 200

        today_screenings = response.json["calendar"][today.isoformat()]
        tomorrow_screenings = response.json["calendar"][tomorrow.isoformat()]
        assert today_screenings[0]["dayScreenings"][0]["stockId"] == today_closest_stock.id
        assert today_screenings[1]["dayScreenings"][0]["stockId"] == today_furthest_stock.id
        assert today_screenings[2]["nextScreening"]["stockId"] == tomorrow_closest_stock.id
        assert today_screenings[3]["nextScreening"]["stockId"] == tomorrow_furthest_stock.id
        assert tomorrow_screenings[0]["dayScreenings"][0]["stockId"] == tomorrow_closest_stock.id
        assert tomorrow_screenings[1]["dayScreenings"][0]["stockId"] == tomorrow_furthest_stock.id
        assert tomorrow_screenings[2]["nextScreening"]["stockId"] == today_closest_stock.id
        assert tomorrow_screenings[3]["nextScreening"]["stockId"] == today_furthest_stock.id

    def test_venue_screenings_are_sorted_by_beginning_datetime(self, client):
        product = offers_factories.ProductFactory(extraData={"allocineId": 12345})
        address = AddressFactory(latitude=48.85, longitude=2.35)
        venue = offerers_factories.VenueFactory(offererAddress__address=address)
        first_stock = offers_factories.EventStockFactory(
            offer__product=product,
            offer__venue=venue,
            beginningDatetime=datetime.now() + timedelta(hours=1),
        )
        last_stock = offers_factories.EventStockFactory(
            offer__product=product,
            offer__venue=venue,
            beginningDatetime=datetime.now() + timedelta(hours=2),
        )

        today = date.today()
        tomorrow = date.today() + timedelta(days=1)
        params = {
            "allocineId": "12345",
            "latitude": 48.85,
            "longitude": 2.35,
            "from": today,
            "to": tomorrow,
        }
        expected_num_queries = 1  # product
        expected_num_queries += 1  # stocks
        expected_num_queries += 1  # screenings
        with assert_num_queries(expected_num_queries):
            response = client.get("/native/v1/movie/calendar", params=params)
            assert response.status_code == 200

        today_screenings = response.json["calendar"][today.isoformat()]
        assert today_screenings[0]["dayScreenings"][0]["stockId"] == first_stock.id
        assert today_screenings[0]["dayScreenings"][1]["stockId"] == last_stock.id

    def test_next_screening_is_closest_from_today(self, client):
        product = offers_factories.ProductFactory(extraData={"allocineId": 12345})
        address = AddressFactory(latitude=48.85, longitude=2.35)
        venue = offerers_factories.VenueFactory(offererAddress__address=address)
        closest_stock_from_tomorrow = offers_factories.EventStockFactory(
            offer__product=product,
            offer__venue=venue,
            beginningDatetime=datetime.now() + timedelta(hours=2),
        )
        _furthest_stock_from_tomorrow = offers_factories.EventStockFactory(
            offer__product=product,
            offer__venue=venue,
            beginningDatetime=datetime.now() + timedelta(days=3, hours=1),
        )

        today = date.today()
        tomorrow = date.today() + timedelta(days=1)
        in_three_days = date.today() + timedelta(days=3)
        params = {
            "allocineId": "12345",
            "latitude": 48.85,
            "longitude": 2.35,
            "from": today,
            "to": in_three_days,
        }
        expected_num_queries = 1  # product
        expected_num_queries += 1  # stocks
        expected_num_queries += 1  # screenings
        with assert_num_queries(expected_num_queries):
            response = client.get("/native/v1/movie/calendar", params=params)
            assert response.status_code == 200

        tomorrow_screenings = response.json["calendar"][tomorrow.isoformat()]
        assert tomorrow_screenings[0]["nextScreening"]["stockId"] == closest_stock_from_tomorrow.id

    def test_screenings_are_within_around_radius(self, client):
        product = offers_factories.ProductFactory(extraData={"allocineId": 12345})
        closest_address = AddressFactory(latitude=48.8, longitude=2.35)
        furthest_address = AddressFactory(latitude=48.0, longitude=2.35)
        _closest_stock = offers_factories.EventStockFactory(
            offer__product=product,
            offer__venue__offererAddress__address=closest_address,
            beginningDatetime=datetime.now() + timedelta(hours=1),
        )
        _furthest_stock = offers_factories.EventStockFactory(
            offer__product=product,
            offer__venue__offererAddress__address=furthest_address,
            beginningDatetime=datetime.now() + timedelta(hours=1),
        )

        start_of_day = datetime.combine(date.today(), time.min)
        end_of_day = datetime.combine(date.today(), time.max)
        params = {
            "allocineId": "12345",
            "latitude": 48.8,
            "longitude": 2.35,
            "aroundRadius": 10_000,
            "from": start_of_day,
            "to": end_of_day,
        }
        expected_num_queries = 1  # product
        expected_num_queries += 1  # stocks
        expected_num_queries += 1  # screenings
        with assert_num_queries(expected_num_queries):
            response = client.get("/native/v1/movie/calendar", params=params)
            assert response.status_code == 200

        today_screenings = response.json["calendar"][start_of_day.date().isoformat()]
        assert len(today_screenings) == 1
        assert len(today_screenings[0]["dayScreenings"]) == 1
        assert today_screenings[0]["distance"] < 10_000


class VenueMovieCalendarTest:
    def test_get_venue_movie_calendar(self, client):
        product = offers_factories.ProductFactory(subcategoryId=subcategories.SEANCE_CINE.id, durationMinutes=116)
        stock = offers_factories.EventStockFactory(
            offer__product=product, beginningDatetime=datetime.now() + timedelta(hours=1)
        )
        today = date.today()
        tomorrow = date.today() + timedelta(days=1)
        venue_id = stock.offer.venue.id
        expected_num_queries = 1  # offers
        with assert_num_queries(expected_num_queries):
            response = client.get(f"/native/v1/venue/{venue_id}/movie/calendar", params={"from": today, "to": tomorrow})
            assert response.status_code == 200

        calendar = response.json["calendar"]
        assert calendar == {
            today.isoformat(): [
                {
                    "duration": 116,
                    "genres": [],
                    "last30DaysBookings": 0,
                    "movieName": stock.offer.name,
                    "offerId": stock.offer.id,
                    "thumbUrl": None,
                    "dayScreenings": [
                        {
                            "beginningDatetime": date_utils.format_into_utc_date(stock.beginningDatetime),
                            "features": [],
                            "price": 10.1,
                            "stockId": stock.id,
                        }
                    ],
                    "nextScreening": {
                        "beginningDatetime": date_utils.format_into_utc_date(stock.beginningDatetime),
                        "features": [],
                        "price": 10.1,
                        "stockId": stock.id,
                    },
                }
            ],
            tomorrow.isoformat(): [
                {
                    "duration": 116,
                    "genres": [],
                    "last30DaysBookings": 0,
                    "movieName": stock.offer.name,
                    "offerId": stock.offer.id,
                    "thumbUrl": None,
                    "dayScreenings": [],
                    "nextScreening": {
                        "beginningDatetime": date_utils.format_into_utc_date(stock.beginningDatetime),
                        "features": [],
                        "price": 10.1,
                        "stockId": stock.id,
                    },
                }
            ],
        }

    def test_day_screenings_are_sorted_by_last_30_days_bookings(self, client):
        tomorrow = datetime.today() + timedelta(days=1)
        beginning_datetime = tomorrow.replace(hour=1)
        movie_day = tomorrow.date()
        day_after = movie_day + timedelta(days=1)
        least_booked_product = offers_factories.ProductFactory(
            last_30_days_booking=1, subcategoryId=subcategories.SEANCE_CINE.id
        )
        most_booked_product = offers_factories.ProductFactory(
            last_30_days_booking=2, subcategoryId=subcategories.SEANCE_CINE.id
        )
        venue = offerers_factories.VenueFactory()
        least_booked_stock = offers_factories.EventStockFactory(
            offer__product=least_booked_product, beginningDatetime=beginning_datetime, offer__venue=venue
        )
        most_booked_stock = offers_factories.EventStockFactory(
            offer__product=most_booked_product, beginningDatetime=beginning_datetime, offer__venue=venue
        )
        venue_id = venue.id
        expected_num_queries = 1  # offers
        with assert_num_queries(expected_num_queries):
            response = client.get(
                f"/native/v1/venue/{venue_id}/movie/calendar", params={"from": movie_day, "to": day_after}
            )
            assert response.status_code == 200

        movie_day_screenings = response.json["calendar"][movie_day.isoformat()]
        assert movie_day_screenings[0]["dayScreenings"][0]["stockId"] == most_booked_stock.id
        assert movie_day_screenings[1]["dayScreenings"][0]["stockId"] == least_booked_stock.id

    def test_day_screenings_are_sorted_by_beginning_datetime(self, client):
        tomorrow = datetime.today() + timedelta(days=1)
        before_screenings = tomorrow.replace(hour=0)
        first_beginning_datetime = tomorrow.replace(hour=1)
        last_beginning_datetime = tomorrow.replace(hour=2)
        after_screenings = tomorrow.replace(hour=3)
        product = offers_factories.ProductFactory(subcategoryId=subcategories.SEANCE_CINE.id)
        offer = offers_factories.OfferFactory(product=product)
        first_screened_stock = offers_factories.EventStockFactory(
            offer=offer, beginningDatetime=first_beginning_datetime
        )
        last_screened_stock = offers_factories.EventStockFactory(offer=offer, beginningDatetime=last_beginning_datetime)
        venue_id = offer.venue.id
        expected_num_queries = 1  # offers
        with assert_num_queries(expected_num_queries):
            response = client.get(
                f"/native/v1/venue/{venue_id}/movie/calendar",
                params={"from": before_screenings, "to": after_screenings},
            )
            assert response.status_code == 200

        tomorrow_screenings = response.json["calendar"][tomorrow.date().isoformat()]
        assert tomorrow_screenings[0]["dayScreenings"][0]["stockId"] == first_screened_stock.id
        assert tomorrow_screenings[0]["dayScreenings"][1]["stockId"] == last_screened_stock.id

    def test_next_screening_is_closest_requested_day(self, client):
        tomorrow = datetime.today() + timedelta(days=1)
        in_two_days = datetime.today() + timedelta(days=2)
        in_three_days = datetime.today() + timedelta(days=3)
        in_four_days = datetime.today() + timedelta(days=4)
        before_screenings = tomorrow.replace(hour=0)
        after_screenings = datetime.today() + timedelta(days=5)
        product = offers_factories.ProductFactory(subcategoryId=subcategories.SEANCE_CINE.id)
        offer = offers_factories.OfferFactory(product=product)
        tomorrow_stock = offers_factories.EventStockFactory(offer=offer, beginningDatetime=tomorrow)
        in_four_days_stock = offers_factories.EventStockFactory(offer=offer, beginningDatetime=in_four_days)

        venue_id = offer.venue.id
        expected_num_queries = 1  # offers
        with assert_num_queries(expected_num_queries):
            response = client.get(
                f"/native/v1/venue/{venue_id}/movie/calendar",
                params={"from": before_screenings, "to": after_screenings},
            )
            assert response.status_code == 200

        calendar = response.json["calendar"]
        assert calendar[in_two_days.date().isoformat()][0]["nextScreening"]["stockId"] == tomorrow_stock.id
        assert calendar[in_three_days.date().isoformat()][0]["nextScreening"]["stockId"] == in_four_days_stock.id

    def test_calendar_is_empty_if_no_screenings_found(self, client):
        tomorrow = (datetime.today() + timedelta(days=1)).date()
        in_two_days = (datetime.today() + timedelta(days=2)).date()
        venue = offerers_factories.VenueFactory()

        venue_id = venue.id
        expected_num_queries = 1  # offers
        with assert_num_queries(expected_num_queries):
            response = client.get(
                f"/native/v1/venue/{venue_id}/movie/calendar", params={"from": tomorrow, "to": in_two_days}
            )
            assert response.status_code == 200

        assert response.json["calendar"] == {tomorrow.isoformat(): [], in_two_days.isoformat(): []}

    def test_calendar_is_empty_if_venue_not_found(self, client):
        tomorrow = (datetime.today() + timedelta(days=1)).date()
        in_two_days = (datetime.today() + timedelta(days=2)).date()

        fake_venue_id = 999999
        expected_num_queries = 1  # offers
        with assert_num_queries(expected_num_queries):
            response = client.get(
                f"/native/v1/venue/{fake_venue_id}/movie/calendar", params={"from": tomorrow, "to": in_two_days}
            )
            assert response.status_code == 200

        assert response.json["calendar"] == {tomorrow.isoformat(): [], in_two_days.isoformat(): []}


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
            beginningDatetime=date_utils.get_naive_utc_now() - timedelta(days=1),
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
        nb_queries += 1  # select opening hours
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
        client = client.with_token(user)

        with assert_no_duplicated_queries():
            response = client.post("/native/v1/send_offer_webapp_link_by_email/98765432123456789")
            assert response.status_code == 404
        assert not mails_testing.outbox

    @pytest.mark.parametrize(
        "validation", [OfferValidationStatus.DRAFT, OfferValidationStatus.PENDING, OfferValidationStatus.REJECTED]
    )
    def test_send_non_approved_offer_webapp_link_by_email(self, client, validation):
        user = users_factories.UserFactory()
        client = client.with_token(user)
        offer_id = offers_factories.OfferFactory(validation=validation).id

        with assert_no_duplicated_queries():
            response = client.post(f"/native/v1/send_offer_webapp_link_by_email/{offer_id}")
            assert response.status_code == 404
        assert not mails_testing.outbox

    def send_request(self, client):
        offer_id = offers_factories.OfferFactory().id
        user = users_factories.BeneficiaryGrant18Factory()
        test_client = client.with_token(user)

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
        client = client.with_token(user)

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
        client = client.with_token(user)

        with assert_no_duplicated_queries():
            response = client.post("/native/v1/send_offer_link_by_push/9999999999")
            assert response.status_code == 404

        assert len(notifications_testing.requests) == 0

    @pytest.mark.parametrize(
        "validation", [OfferValidationStatus.DRAFT, OfferValidationStatus.PENDING, OfferValidationStatus.REJECTED]
    )
    def test_send_non_approved_offer_link_notification(self, client, validation):
        user = users_factories.UserFactory()
        client = client.with_token(user)
        offer_id = offers_factories.OfferFactory(validation=validation).id

        with assert_no_duplicated_queries():
            response = client.post(f"/native/v1/send_offer_link_by_push/{offer_id}")
            assert response.status_code == 404

        assert len(notifications_testing.requests) == 0


class OfferReportReasonsTest:
    def test_get_reasons(self, app, client):
        user = UserFactory()
        response = client.with_token(user).get("/native/v1/offer/report/reasons")

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
