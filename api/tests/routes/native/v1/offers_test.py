from datetime import datetime
from datetime import timedelta

from freezegun import freeze_time
import pytest

from pcapi import settings
from pcapi.core.bookings.factories import BookingFactory
from pcapi.core.categories import subcategories
from pcapi.core.categories import subcategories_v2
import pcapi.core.mails.testing as mails_testing
from pcapi.core.offers.factories import EventStockFactory
from pcapi.core.offers.factories import MediationFactory
from pcapi.core.offers.factories import OfferFactory
from pcapi.core.offers.factories import OfferReportFactory
from pcapi.core.offers.factories import ProductFactory
from pcapi.core.offers.factories import StockWithActivationCodesFactory
from pcapi.core.offers.factories import ThingStockFactory
from pcapi.core.offers.models import OfferReport
from pcapi.core.testing import assert_num_queries
from pcapi.core.testing import override_features
from pcapi.core.users import factories as users_factories
from pcapi.core.users.factories import UserFactory
import pcapi.notifications.push.testing as notifications_testing

from tests.conftest import TestClient

from .utils import create_user_and_test_client


pytestmark = pytest.mark.usefixtures("db_session")


class OffersTest:
    @freeze_time("2020-01-01")
    def test_get_event_offer(self, app):
        extra_data = {
            "author": "mandibule",
            "isbn": "3838",
            "musicSubType": "502",
            "musicType": "501",
            "performer": "interprète",
            "showSubType": "101",
            "showType": "100",
            "stageDirector": "metteur en scène",
            "speaker": "intervenant",
            "visa": "vasi",
        }
        offer = OfferFactory(
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
        MediationFactory(id=111, offer=offer, thumbCount=1, credit="street credit")

        bookableStock = EventStockFactory(offer=offer, price=12.34, quantity=2)
        expiredStock = EventStockFactory(
            offer=offer, price=45.68, beginningDatetime=datetime.utcnow() - timedelta(days=1)
        )
        exhaustedStock = EventStockFactory(offer=offer, price=89.00, quantity=1)

        BookingFactory(stock=bookableStock)
        BookingFactory(stock=exhaustedStock)

        offer_id = offer.id
        queries = 1  # select offer
        queries += 1  # select feature
        with assert_num_queries(queries):
            response = TestClient(app.test_client()).get(f"/native/v1/offer/{offer_id}")

        assert response.status_code == 200
        response_content = response.json
        response_content["stocks"].sort(key=lambda stock: stock["price"])

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
                    "id": bookableStock.id,
                    "price": 1234,
                    "beginningDatetime": "2020-01-06T00:00:00Z",
                    "bookingLimitDatetime": "2020-01-05T23:00:00Z",
                    "cancellationLimitDatetime": "2020-01-03T00:00:00Z",
                    "isBookable": True,
                    "isForbiddenToUnderage": False,
                    "isSoldOut": False,
                    "isExpired": False,
                    "activationCode": None,
                },
                {
                    "id": expiredStock.id,
                    "price": 4568,
                    "beginningDatetime": "2019-12-31T00:00:00Z",
                    "bookingLimitDatetime": "2019-12-30T23:00:00Z",
                    "cancellationLimitDatetime": "2020-01-01T00:00:00Z",
                    "isBookable": False,
                    "isForbiddenToUnderage": False,
                    "isSoldOut": True,
                    "isExpired": True,
                    "activationCode": None,
                },
                {
                    "id": exhaustedStock.id,
                    "price": 8900,
                    "beginningDatetime": "2020-01-06T00:00:00Z",
                    "bookingLimitDatetime": "2020-01-05T23:00:00Z",
                    "cancellationLimitDatetime": "2020-01-03T00:00:00Z",
                    "isBookable": False,
                    "isForbiddenToUnderage": False,
                    "isSoldOut": True,
                    "isExpired": False,
                    "activationCode": None,
                },
            ],
            key=lambda stock: stock["id"],
        )
        assert response.json["description"] == "desk cryption"
        assert response.json["externalTicketOfficeUrl"] == "https://url.com"
        assert response.json["expenseDomains"] == ["all"]
        assert response.json["extraData"] == {
            "author": "mandibule",
            "isbn": "3838",
            "durationMinutes": 33,
            "musicSubType": "Acid Jazz",
            "musicType": "Jazz",
            "performer": "interprète",
            "showSubType": "Carnaval",
            "showType": "Arts de la rue",
            "speaker": "intervenant",
            "stageDirector": "metteur en scène",
            "visa": "vasi",
        }
        assert response.json["image"] == {
            "url": "http://localhost/storage/thumbs/mediations/N4",
            "credit": "street credit",
        }
        assert response.json["isExpired"] == False
        assert response.json["isForbiddenToUnderage"] == False
        assert response.json["isSoldOut"] == False
        assert response.json["isDuo"] == True
        assert response.json["isEducational"] == False
        assert response.json["isDigital"] == False
        assert response.json["isReleased"] == True
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
            "postalCode": "75000",
            "publicName": "il est venu le temps des names",
            "isPermanent": False,
        }
        assert response.json["withdrawalDetails"] == "modalité de retrait"

    def test_get_thing_offer(self, app):
        product = ProductFactory(thumbCount=1, subcategoryId=subcategories.ABO_MUSEE.id)
        offer = OfferFactory(product=product, venue__isPermanent=True)
        ThingStockFactory(offer=offer, price=12.34)

        offer_id = offer.id
        queries = 1  # select offer
        queries += 1  # select feature
        with assert_num_queries(queries):
            response = TestClient(app.test_client()).get(f"/native/v1/offer/{offer_id}")

        assert response.status_code == 200
        assert not response.json["stocks"][0]["beginningDatetime"]
        assert response.json["stocks"][0]["price"] == 1234
        assert response.json["subcategoryId"] == "ABO_MUSEE"
        assert response.json["isEducational"] is False
        assert not response.json["isExpired"]
        assert response.json["venue"]["isPermanent"]

    def test_get_digital_offer_with_available_activation_and_no_expiration_date(self, app):
        # given
        stock = StockWithActivationCodesFactory()
        offer_id = stock.offer.id

        queries = 1  # select offer
        queries += 1  # get available_activation_code for each offer.stocks
        queries += 1  # select feature

        # when
        with assert_num_queries(queries):
            response = TestClient(app.test_client()).get(f"/native/v1/offer/{offer_id}")

        # then
        assert response.status_code == 200
        assert response.json["stocks"][0]["activationCode"] == {"expirationDate": None}

    def test_get_digital_offer_with_available_activation_code_and_expiration_date(self, app):
        # given
        stock = StockWithActivationCodesFactory(activationCodes__expirationDate=datetime(2050, 1, 1))
        offer_id = stock.offer.id

        queries = 1  # select offer
        queries += 1  # get available_activation_code for each offer.stocks
        queries += 1  # select feature

        # when
        with assert_num_queries(queries):
            response = TestClient(app.test_client()).get(f"/native/v1/offer/{offer_id}")

        # then
        assert response.status_code == 200
        assert response.json["stocks"][0]["activationCode"] == {"expirationDate": "2050-01-01T00:00:00Z"}

    def test_get_digital_offer_without_available_activation_code(self, app):
        # given
        stock = StockWithActivationCodesFactory(activationCodes__expirationDate=datetime(2000, 1, 1))
        offer_id = stock.offer.id

        queries = 1  # select offer
        queries += 1  # get available_activation_code for each offer.stocks
        queries += 1  # select feature

        # when
        with assert_num_queries(queries):
            response = TestClient(app.test_client()).get(f"/native/v1/offer/{offer_id}")

        # then
        assert response.status_code == 200
        assert response.json["stocks"][0]["activationCode"] is None

    @freeze_time("2020-01-01")
    def test_get_expired_offer(self, app):
        stock = EventStockFactory(beginningDatetime=datetime.utcnow() - timedelta(days=1))

        offer_id = stock.offer.id
        queries = 1  # select offer
        queries += 1  # select feature
        with assert_num_queries(queries):
            response = TestClient(app.test_client()).get(f"/native/v1/offer/{offer_id}")

        assert response.json["isExpired"]

    def test_get_offer_not_found(self, app):
        response = TestClient(app.test_client()).get("/native/v1/offer/1")

        assert response.status_code == 404


class SendOfferWebAppLinkTest:
    def test_sendinblue_send_offer_webapp_link_by_email(self, client):
        """
        Test that email can be sent with SiB and that the link does not
        use the redirection domain (not activated by default)
        """
        mail = self.send_request(client)
        assert mail.sent_data["params"]["OFFER_WEBAPP_LINK"].startswith(settings.WEBAPP_V2_URL)

    @override_features(ENABLE_IOS_OFFERS_LINK_WITH_REDIRECTION=True)
    def test_send_offer_webapp_link_by_email_with_redirection_link(self, client):
        """
        Test that the redirection domain is used, once the FF has been
        activated.
        """
        mail = self.send_request(client)
        assert mail.sent_data["params"]["OFFER_WEBAPP_LINK"].startswith(settings.WEBAPP_V2_REDIRECT_URL)

    def test_send_offer_webapp_link_by_email_not_found(self, app):
        _, test_client = create_user_and_test_client(app)

        # expected queries:
        #   * get User
        #   * try to find Offer
        with assert_num_queries(2):
            response = test_client.post("/native/v1/send_offer_webapp_link_by_email/98765432123456789")
            assert response.status_code == 404
        assert not mails_testing.outbox

    def send_request(self, client):
        offer_id = OfferFactory().id
        user = users_factories.BeneficiaryGrant18Factory()
        test_client = client.with_token(user.email)

        # expected queries:
        #   * get User
        #   * find Offer
        #   * get FF ENABLE_IOS_OFFERS_LINK_WITH_REDIRECTION.isactive
        with assert_num_queries(3):
            response = test_client.post(f"/native/v1/send_offer_webapp_link_by_email/{offer_id}")
            assert response.status_code == 204

        assert len(mails_testing.outbox) == 1

        mail = mails_testing.outbox[0]
        assert mail.sent_data["To"] == user.email

        return mail


class SendOfferLinkNotificationTest:
    def test_send_offer_link_notification(self, app):
        """
        Test that a push notification to the user is send with a link to the
        offer.
        """
        # offer.id must be used before the assert_num_queries context manager
        # because it triggers a SQL query.
        offer = OfferFactory()
        offer_id = offer.id

        user, test_client = create_user_and_test_client(app)

        # expected queries:
        #   * get user
        #   * get offer
        with assert_num_queries(2):
            response = test_client.post(f"/native/v1/send_offer_link_by_push/{offer_id}")
            assert response.status_code == 204

        assert len(notifications_testing.requests) == 1

        notification = notifications_testing.requests[0]
        assert notification["user_ids"] == [user.id]

        assert offer.name in notification["message"]["title"]

    def test_send_offer_link_notification_not_found(self, app):
        """Test that no push notification is sent when offer is not found"""
        _, test_client = create_user_and_test_client(app)

        # expected queries:
        #   * get user
        #   * search for offer
        with assert_num_queries(2):
            response = test_client.post("/native/v1/send_offer_link_by_push/9999999999")
            assert response.status_code == 404

        assert len(notifications_testing.requests) == 0


class ReportOfferTest:
    def test_report_offer(self, app):
        user, test_client = create_user_and_test_client(app)
        offer = OfferFactory()

        # expected queries:
        #   * select offer
        #   * get user
        #   * insert report
        #   * release savepoint
        #
        #   * reload user
        #   * select offer
        with assert_num_queries(6):
            response = test_client.post(f"/native/v1/offer/{offer.id}/report", json={"reason": "INAPPROPRIATE"})
            assert response.status_code == 204

        assert OfferReport.query.count() == 1
        report = OfferReport.query.first()

        assert report.user == user
        assert report.offer == offer

        assert len(mails_testing.outbox) == 1

        email = mails_testing.outbox[0]
        assert email.sent_data["To"] == "report_offer@example.com"
        assert email.sent_data["params"]["USER_ID"] == user.id
        assert email.sent_data["params"]["OFFER_ID"] == offer.id

    def test_report_offer_with_custom_reason(self, app):
        user, test_client = create_user_and_test_client(app)
        offer = OfferFactory()

        # expected queries:
        #   * select offer
        #   * get user
        #   * insert report
        #   * release savepoint
        #
        #   * reload user
        #   * select offer
        with assert_num_queries(6):
            data = {"reason": "OTHER", "customReason": "saynul"}
            response = test_client.post(f"/native/v1/offer/{offer.id}/report", json=data)
            assert response.status_code == 204

        assert OfferReport.query.count() == 1
        report = OfferReport.query.first()

        assert report.user == user
        assert report.offer == offer

        assert len(mails_testing.outbox) == 1

        email = mails_testing.outbox[0]
        assert email.sent_data["To"] == "support@example.com"
        assert email.sent_data["params"]["USER_ID"] == user.id
        assert email.sent_data["params"]["OFFER_ID"] == offer.id
        assert "saynul" in email.sent_data["params"]["REASON"]
        assert "OFFER_URL" in email.sent_data["params"]

    def test_report_offer_twice(self, app):
        user, test_client = create_user_and_test_client(app)
        offer = OfferFactory()

        OfferReportFactory(user=user, offer=offer)

        # expected queries:
        #   * get user
        #   * get offer
        #   * rollback
        with assert_num_queries(3):
            response = test_client.post(f"/native/v1/offer/{offer.id}/report", json={"reason": "PRICE_TOO_HIGH"})
            assert response.status_code == 400
            assert response.json["code"] == "OFFER_ALREADY_REPORTED"

        assert OfferReport.query.count() == 1  # no new report
        assert not mails_testing.outbox

    def test_report_offer_malformed(self, app, client):
        user = UserFactory()
        offer = OfferFactory()

        # user.email triggers an SQL request, same for offer.id
        # therefore, these attributes should be read outside of the
        # assert_num_queries() block
        email = user.email
        offer_id = offer.id

        # expected queries:
        #   * get user
        #   * rollback
        with assert_num_queries(2):
            dst = f"/native/v1/offer/{offer_id}/report"
            response = client.with_token(email).post(dst, json={"reason": "OTHER"})
            assert response.status_code == 400
            assert response.json["code"] == "REPORT_MALFORMED"

        assert OfferReport.query.count() == 0  # no new report
        assert not mails_testing.outbox

    def test_report_offer_custom_reason_too_long(self, app, client):
        offer = OfferFactory()
        offer_id = offer.id

        with assert_num_queries(0):
            data = {"reason": "OTHER", "customReason": "a" * 513}
            response = client.post(f"/native/v1/offer/{offer_id}/report", json=data)
            assert response.status_code == 400
            assert response.json["customReason"] == ["custom reason is too long"]

        assert OfferReport.query.count() == 0  # no new report
        assert not mails_testing.outbox

    def test_report_offer_unknown_reason(self, app, client):
        offer = OfferFactory()
        offer_id = offer.id

        with assert_num_queries(0):
            data = {"reason": "UNKNOWN"}
            response = client.post(f"/native/v1/offer/{offer_id}/report", json=data)
            assert response.status_code == 400
            assert response.json["reason"] == ["unknown reason"]

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
        offers = OfferFactory.create_batch(3)
        reports = [
            OfferReportFactory(user=user, offer=offers[0]),
            OfferReportFactory(user=user, offer=offers[1]),
        ]

        # offers reported by this user should not be returned
        another_user = UserFactory()
        OfferReportFactory(user=another_user, offer=offers[2])

        client.with_token(user.email)
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
        OfferFactory()

        client.with_token(user.email)
        response = client.get("/native/v1/offers/reports")

        assert response.status_code == 200
        assert not response.json["reportedOffers"]


class SubcategoriesTest:
    def test_get_subcategories(self, app):
        with assert_num_queries(0):
            response = TestClient(app.test_client()).get("/native/v1/subcategories")

        assert response.status_code == 200
        assert list(response.json.keys()) == ["subcategories", "searchGroups", "homepageLabels"]
        assert len(response.json["subcategories"]) == len(subcategories.ALL_SUBCATEGORIES)
        assert len(response.json["searchGroups"]) == len(subcategories.SearchGroups)
        assert len(response.json["homepageLabels"]) == len(subcategories.HomepageLabels)
        assert all(
            list(subcategory_dict.keys())
            == [
                "id",
                "categoryId",
                "appLabel",
                "searchGroupName",
                "homepageLabelName",
                "isEvent",
                "onlineOfflinePlatform",
            ]
            for subcategory_dict in response.json["subcategories"]
        )
        assert all(
            list(search_group_dict.keys())
            == [
                "name",
                "value",
            ]
            for search_group_dict in response.json["searchGroups"]
        )
        assert all(
            list(homepage_label_dict.keys())
            == [
                "name",
                "value",
            ]
            for homepage_label_dict in response.json["homepageLabels"]
        )

    def test_get_subcategories_v2(self, client):
        with assert_num_queries(0):
            response = client.get("/native/v1/subcategories/v2")

        assert response.status_code == 200

        assert set(response.json.keys()) == {"subcategories", "searchGroups", "homepageLabels"}

        found_subcategory_ids = {x["id"] for x in response.json["subcategories"]}
        expected_subcategory_ids = {x.id for x in subcategories_v2.ALL_SUBCATEGORIES}
        assert found_subcategory_ids == expected_subcategory_ids

        found_search_group_names = {x["name"] for x in response.json["searchGroups"]}
        expected_search_group_names = {x.search_group_name for x in subcategories_v2.ALL_SUBCATEGORIES}
        assert found_search_group_names == expected_search_group_names

        found_home_labels = {x["name"] for x in response.json["homepageLabels"]}
        expected_home_labels = {x.homepage_label_name for x in subcategories_v2.ALL_SUBCATEGORIES}
        assert found_home_labels == expected_home_labels
