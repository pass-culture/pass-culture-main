from datetime import datetime
from datetime import timedelta

import pytest
import time_machine

import pcapi.core.chronicles.factories as chronicles_factories
import pcapi.core.chronicles.models as chronicles_models
import pcapi.core.mails.testing as mails_testing
import pcapi.core.offers.factories as offers_factories
from pcapi import settings
from pcapi.core.bookings.factories import BookingFactory
from pcapi.core.categories import subcategories
from pcapi.core.external.batch import testing as notifications_testing
from pcapi.core.providers.etls.cinema_etl_template import ShowFeatures
from pcapi.core.testing import assert_no_duplicated_queries
from pcapi.core.testing import assert_num_queries
from pcapi.core.users import factories as users_factories
from pcapi.models import db
from pcapi.models.offer_mixin import OfferValidationStatus
from pcapi.utils import date as date_utils


pytestmark = pytest.mark.usefixtures("db_session")


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
            priceCategory__label="bookable",
            features=[
                ShowFeatures.VF.value,
                ShowFeatures.THREE_D.value,
                ShowFeatures.ICE.value,
            ],
        )
        another_bookable_stock = offers_factories.EventStockFactory(
            offer=offer,
            price=12.34,
            quantity=3,
            priceCategory=bookable_stock.priceCategory,
            features=[
                ShowFeatures.VO.value,
                ShowFeatures.THREE_D.value,
            ],
        )
        expired_stock = offers_factories.EventStockFactory(
            offer=offer,
            price=45.67,
            beginningDatetime=date_utils.get_naive_utc_now() - timedelta(days=1),
            priceCategory__label="expired",
            features=[
                ShowFeatures.VF.value,
                ShowFeatures.ICE.value,
            ],
        )
        exhausted_stock = offers_factories.EventStockFactory(
            offer=offer,
            price=89.00,
            quantity=1,
            priceCategory__label="exhausted",
            features=[ShowFeatures.VO.value],
        )

        BookingFactory(stock=bookable_stock, user__deposit__expirationDate=datetime(year=2031, month=12, day=31))
        BookingFactory(stock=exhausted_stock, user__deposit__expirationDate=datetime(year=2031, month=12, day=31))

        payload = {"offer_ids": [offer.id]}

        nb_queries = 1  # select offer
        nb_queries += 1  # select stocks
        nb_queries += 1  # select mediations
        nb_queries += 1  # select chronicles
        with assert_num_queries(nb_queries, expire_session=False):
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

        assert response_offer["publicationDate"] is None
        assert response_offer["bookingAllowedDatetime"] is None


class SendOfferWebAppLinkTest:
    def test_brevo_send_offer_webapp_link_by_email(self, client):
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
        Test that a push notification to the user is sent with a link to the
        offer.
        """
        # offer.id must be used before the assert_num_queries context manager
        # because it triggers a SQL query.
        offer = offers_factories.OfferFactory()
        offer_id = offer.id

        user = users_factories.UserFactory()
        client = client.with_token(user)

        num_queries = 1  # select user
        num_queries += 1  # select offer in route
        with assert_num_queries(2):
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
        club_types = [chronicle["clubType"] for chronicle in response.json["chronicles"]]
        assert club_types == ["BOOK", "BOOK"]

    def test_get_offer_scene_club_chronicles(self, client):
        offer = offers_factories.OfferFactory(subcategoryId=subcategories.SPECTACLE_REPRESENTATION.id)
        chronicles_factories.ChronicleFactory(
            offers=[offer],
            content="Test Scene Chronicle",
            clubType=chronicles_models.ChronicleClubType.SCENE_CLUB,
            productIdentifierType=chronicles_models.ChronicleProductIdentifierType.OFFER_ID,
            productIdentifier=str(offer.id),
            isActive=True,
            isSocialMediaDiffusible=True,
        )

        offer_id = offer.id
        db.session.expire_all()
        with assert_num_queries(self.expected_num_queries):
            response = client.get(f"/native/v1/offer/{offer_id}/chronicles")
        assert response.status_code == 200

        chronicles = response.json["chronicles"]
        assert len(chronicles) == 1
        assert chronicles[0]["content"] == "Test Scene Chronicle"
        assert chronicles[0]["clubType"] == "SCENE"

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

        long_text = """Vesper is a world built on the ruins of older ones: in the dark of that colossal cavern no one has ever known the edges of, empires rise and fall like flickering candles.

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
