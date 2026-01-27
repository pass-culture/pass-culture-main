import logging
from datetime import datetime
from datetime import timedelta

import pytest
import time_machine

import pcapi.core.artist.factories as artists_factories
import pcapi.core.chronicles.factories as chronicles_factories
import pcapi.core.offers.factories as offers_factories
import pcapi.core.providers.factories as providers_factories
import pcapi.local_providers.cinema_providers.constants as cinema_providers_constants
from pcapi import settings
from pcapi.core.bookings.factories import BookingFactory
from pcapi.core.categories import subcategories
from pcapi.core.geography.factories import AddressFactory
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offerers.factories import OffererAddressFactory
from pcapi.core.offerers.factories import VenueFactory
from pcapi.core.offers.models import ImageType
from pcapi.core.providers.constants import BookFormat
from pcapi.core.providers.repository import get_provider_by_local_class
from pcapi.core.reactions.factories import ReactionFactory
from pcapi.core.reactions.models import ReactionTypeEnum
from pcapi.core.testing import assert_num_queries
from pcapi.models.offer_mixin import OfferValidationStatus
from pcapi.routes.native.v1.serialization.offers import MAX_PREVIEW_CHRONICLES
from pcapi.utils import date as date_utils


pytestmark = pytest.mark.usefixtures("db_session")


class OffersV3Test:
    base_num_queries = 1  # select offer with joins
    base_num_queries += 1  # select mediations (selectinload)
    base_num_queries += 1  # select stocks (selectinload)
    base_num_queries += 1  # select chronicles (selectinload)

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
            "cast": ["cast1", "cast2"],
            "certificate": "Interdit aux moins de 18 ans",
            "editeur": "editeur",
            "genres": ["ACTION", "DRAMA"],
            "gtl_id": "01030000",
            "musicSubType": "502",
            "musicType": "501",
            "performer": "interprète",
            "releaseDate": "2020-01-01",
            "showSubType": "101",
            "showType": "100",
            "speaker": "intervenant",
            "stageDirector": "metteur en scène",
            "visa": "vasi",
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
            response = client.get(f"/native/v3/offer/{offer_id}")

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
            response = client.get(f"/native/v3/offer/{offer_id}")

        assert response.status_code == 200
        assert response.json["stocks"][0]["remainingQuantity"] is None

    def test_get_thing_offer(self, client):
        offer = offers_factories.OfferFactory(venue__isPermanent=True, subcategoryId=subcategories.CARTE_MUSEE.id)
        offers_factories.ThingStockFactory(offer=offer, price=12.34)

        offer_id = offer.id
        with assert_num_queries(self.base_num_queries):
            response = client.get(f"/native/v3/offer/{offer_id}")

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
            response = client.get(f"/native/v3/offer/{offer_id}")

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
            response = client.get(f"/native/v3/offer/{offer_id}")

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
            response = client.get(f"/native/v3/offer/{offer_id}")

        # then
        assert response.status_code == 200
        assert response.json["stocks"][0]["activationCode"] is None

    @time_machine.travel("2020-01-01")
    def test_get_expired_offer(self, client):
        stock = offers_factories.EventStockFactory(beginningDatetime=date_utils.get_naive_utc_now() - timedelta(days=1))

        offer_id = stock.offer.id
        with assert_num_queries(self.base_num_queries):
            response = client.get(f"/native/v3/offer/{offer_id}")

        assert response.json["isExpired"]

    def test_get_offer_not_found(self, client):
        # 1. select offer
        # 2. rollback
        # 3. rollback
        with assert_num_queries(3):
            response = client.get("/native/v3/offer/1")

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
            response = client.get(f"/native/v3/offer/{offer_id}")
            assert response.status_code == 404

    def test_get_closed_offerer_offer(self, client):
        offer = offers_factories.EventOfferFactory(venue__managingOfferer=offerers_factories.ClosedOffererFactory())
        offers_factories.EventStockFactory(offer=offer)

        offer_id = offer.id
        with assert_num_queries(self.base_num_queries):
            response = client.get(f"/native/v3/offer/{offer_id}")
            assert response.status_code == 200

        assert response.json["isReleased"] is False

    def should_have_metadata_describing_the_offer(self, client):
        offer = offers_factories.ThingOfferFactory()

        offer_id = offer.id
        with assert_num_queries(self.base_num_queries):
            response = client.get(f"/native/v3/offer/{offer_id}")

        assert isinstance(response.json["metadata"], dict)
        assert response.json["metadata"]["@type"] == "Product"

    def should_not_return_soft_deleted_offer(self, client):
        offer = offers_factories.OfferFactory()
        offers_factories.StockFactory(offer=offer, quantity=1, isSoftDeleted=True)
        non_deleted_stock = offers_factories.StockFactory(offer=offer, quantity=1)

        offer_id = offer.id
        with assert_num_queries(self.base_num_queries):
            response = client.get(f"/native/v3/offer/{offer_id}")

        assert response.status_code == 200
        assert len(response.json["stocks"]) == 1
        assert response.json["stocks"][0]["id"] == non_deleted_stock.id

    def should_not_update_offer_stocks_when_getting_offer(self, client):
        offer = offers_factories.OfferFactory()
        offers_factories.StockFactory(offer=offer, quantity=1, isSoftDeleted=True)
        offers_factories.StockFactory(offer=offer, quantity=1)

        offer_id = offer.id
        with assert_num_queries(self.base_num_queries):
            response = client.get(f"/native/v3/offer/{offer_id}")

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
            response = client.get(f"/native/v3/offer/{offer_id}")

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
            response = client.get(f"/native/v3/offer/{offer_id}")

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
            response = client.get(f"/native/v3/offer/{offer_id}")

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
            response = client.get(f"/native/v3/offer/{offer_id}")

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
            response = client.get(f"/native/v3/offer/{offer_id}")

        assert response.status_code == 200
        assert response.json["likesCount"] == 2

    def test_get_offer_attached_to_product_with_user_reaction(self, client):
        product = offers_factories.ProductFactory(subcategoryId=subcategories.SEANCE_CINE.id)
        offer = offers_factories.EventOfferFactory(product=product)
        offers_factories.EventStockFactory(offer=offer, price=12.34)
        ReactionFactory(product=product, reactionType=ReactionTypeEnum.LIKE)
        ReactionFactory(product=product, reactionType=ReactionTypeEnum.LIKE)
        ReactionFactory(product=product, reactionType=ReactionTypeEnum.DISLIKE)

        offer_id = offer.id
        with assert_num_queries(self.base_num_queries + self.num_queries_with_product):
            response = client.get(f"/native/v3/offer/{offer_id}")

        assert response.status_code == 200
        assert response.json["likesCount"] == 2

    def test_get_event_offer_with_no_reactions(self, client):
        offer = offers_factories.EventOfferFactory(subcategoryId=subcategories.SEANCE_CINE.id)
        offers_factories.EventStockFactory(offer=offer, price=12.34)

        offer_id = offer.id
        with assert_num_queries(self.base_num_queries):
            response = client.get(f"/native/v3/offer/{offer_id}")

        assert response.status_code == 200
        assert response.json["likesCount"] == 0

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
            response = client.get(f"/native/v3/offer/{offer_id}")

        assert response.status_code == 200
        assert response.json["isExternalBookingsDisabled"] is booking_disabled

    def test_offers_has_own_address(self, client):
        address = AddressFactory()
        oa = OffererAddressFactory(address=address)
        offer = offers_factories.OfferFactory(offererAddress=oa)

        offer_id = offer.id
        with assert_num_queries(self.base_num_queries):
            response = client.get(f"/native/v3/offer/{offer_id}/")
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
            response = client.get(f"/native/v3/offer/{offer_id}")
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
            response = client.get(f"/native/v3/offer/{offer_id}")
        assert response.status_code == 200
        assert response.json["extraData"]["bookFormat"] == "Poche"

    def test_offer_extra_data_book_format(self, client):
        extra_data = {"bookFormat": BookFormat.MOYEN_FORMAT}
        offer = offers_factories.OfferFactory(extraData=extra_data)

        offer_id = offer.id
        with assert_num_queries(self.base_num_queries):
            response = client.get(f"/native/v3/offer/{offer_id}")
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
            response = client.get(f"/native/v3/offer/{offer_id}")

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
            response = client.get(f"/native/v3/offer/{offer_id}")

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
            response = client.get(f"/native/v3/offer/{offer_id}")
            assert response.status_code == 200
            assert len(response.json["chronicles"]) == 1

        chronicle = response.json["chronicles"][0]
        assert chronicle["author"] is None

    def test_future_offer(self, client):
        booking_allowed_datetime = datetime(2050, 1, 1)
        offer = offers_factories.OfferFactory(bookingAllowedDatetime=booking_allowed_datetime)

        offer_id = offer.id
        with assert_num_queries(self.base_num_queries):
            response = client.get(f"/native/v3/offer/{offer_id}")

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
            response = client.get(f"/native/v3/offer/{offer_id}")

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
            response = client.get(f"/native/v3/offer/{offer_id}")

        assert response.status_code == 200
        assert response.json["isHeadline"] is False

    def test_get_not_headline_offer(self, client):
        headline_offer = offers_factories.HeadlineOfferFactory()
        offer_id = headline_offer.offer.id

        with assert_num_queries(self.base_num_queries):
            response = client.get(f"/native/v3/offer/{offer_id}")

        assert response.status_code == 200
        assert response.json["isHeadline"] is True

    def test_return_venue_public_name(self, client):
        venue = VenueFactory(name="Legal name", publicName="Public name")
        offer_id = offers_factories.OfferFactory(venue=venue).id

        response = client.get(f"/native/v3/offer/{offer_id}")

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
            response = client.get(f"/native/v3/offer/{offer_id}")

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
            response = client.get(f"/native/v3/offer/{offer_id}")
            assert (
                caplog.messages[0]
                == "This offer has a video URL but no videoExternalId in its metaData, and this should not happen"
            )
            assert caplog.records[0].extra == {"offer_id": offer_id}

        assert response.json["video"] is None
