from datetime import datetime
from datetime import timedelta
from unittest import mock
from unittest.mock import patch

from freezegun import freeze_time
import pytest

from pcapi import settings
from pcapi.core.bookings.factories import BookingFactory
from pcapi.core.categories import subcategories
from pcapi.core.categories import subcategories_v2
import pcapi.core.mails.testing as mails_testing
import pcapi.core.offers.factories as offers_factories
from pcapi.core.offers.models import OfferReport
import pcapi.core.providers.factories as providers_factories
from pcapi.core.providers.repository import get_provider_by_local_class
from pcapi.core.testing import assert_no_duplicated_queries
from pcapi.core.testing import assert_num_queries
from pcapi.core.testing import override_features
from pcapi.core.users import factories as users_factories
from pcapi.core.users.factories import UserFactory
from pcapi.models.offer_mixin import OfferValidationStatus
import pcapi.notifications.push.testing as notifications_testing

from tests.conftest import TestClient
from tests.connectors.cgr import soap_definitions
from tests.local_providers.cinema_providers.boost import fixtures as boost_fixtures
from tests.local_providers.cinema_providers.cgr import fixtures as cgr_fixtures

from .utils import create_user_and_test_client


pytestmark = pytest.mark.usefixtures("db_session")


class OffersTest:
    @freeze_time("2020-01-01")
    def test_get_event_offer(self, app):
        extra_data = {
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
        )
        another_bookable_stock = offers_factories.EventStockFactory(
            offer=offer,
            price=12.34,
            quantity=3,
            priceCategory=bookable_stock.priceCategory,
        )
        expired_stock = offers_factories.EventStockFactory(
            offer=offer,
            price=45.67,
            beginningDatetime=datetime.utcnow() - timedelta(days=1),
            priceCategory__priceCategoryLabel__label="expired",
        )
        exhausted_stock = offers_factories.EventStockFactory(
            offer=offer,
            price=89.00,
            quantity=1,
            priceCategory__priceCategoryLabel__label="exhausted",
        )

        BookingFactory(stock=bookable_stock, user__deposit__expirationDate=datetime(year=2031, month=12, day=31))
        BookingFactory(stock=exhausted_stock, user__deposit__expirationDate=datetime(year=2031, month=12, day=31))

        offer_id = offer.id
        with assert_no_duplicated_queries():
            response = TestClient(app.test_client()).get(f"/native/v1/offer/{offer_id}")

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
            "author": "mandibule",
            "isbn": "3838",
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

    def test_get_offer_with_unlimited_stock(self, client):
        product = offers_factories.ProductFactory(thumbCount=1, subcategoryId=subcategories.ABO_MUSEE.id)
        offer = offers_factories.OfferFactory(product=product, venue__isPermanent=True)
        offers_factories.ThingStockFactory(offer=offer, price=12.34, quantity=None)

        with assert_no_duplicated_queries():
            response = client.get(f"/native/v1/offer/{offer.id}")

        assert response.status_code == 200
        assert response.json["stocks"][0]["remainingQuantity"] is None

    def test_get_thing_offer(self, app):
        product = offers_factories.ProductFactory(thumbCount=1, subcategoryId=subcategories.ABO_MUSEE.id)
        offer = offers_factories.OfferFactory(product=product, venue__isPermanent=True)
        offers_factories.ThingStockFactory(offer=offer, price=12.34)

        offer_id = offer.id
        with assert_no_duplicated_queries():
            response = TestClient(app.test_client()).get(f"/native/v1/offer/{offer_id}")

        assert response.status_code == 200
        assert not response.json["stocks"][0]["beginningDatetime"]
        assert response.json["stocks"][0]["price"] == 1234
        assert response.json["stocks"][0]["priceCategoryLabel"] == None
        assert response.json["stocks"][0]["remainingQuantity"] == 1000
        assert response.json["subcategoryId"] == "ABO_MUSEE"
        assert response.json["isEducational"] is False
        assert not response.json["isExpired"]
        assert response.json["venue"]["isPermanent"]

    def test_get_digital_offer_with_available_activation_and_no_expiration_date(self, app):
        # given
        stock = offers_factories.StockWithActivationCodesFactory()
        offer_id = stock.offer.id

        # when
        with assert_no_duplicated_queries():
            response = TestClient(app.test_client()).get(f"/native/v1/offer/{offer_id}")

        # then
        assert response.status_code == 200
        assert response.json["stocks"][0]["activationCode"] == {"expirationDate": None}

    def test_get_digital_offer_with_available_activation_code_and_expiration_date(self, app):
        # given
        stock = offers_factories.StockWithActivationCodesFactory(activationCodes__expirationDate=datetime(2050, 1, 1))
        offer_id = stock.offer.id

        # when
        with assert_no_duplicated_queries():
            response = TestClient(app.test_client()).get(f"/native/v1/offer/{offer_id}")

        # then
        assert response.status_code == 200
        assert response.json["stocks"][0]["activationCode"] == {"expirationDate": "2050-01-01T00:00:00Z"}

    def test_get_digital_offer_without_available_activation_code(self, app):
        # given
        stock = offers_factories.StockWithActivationCodesFactory(activationCodes__expirationDate=datetime(2000, 1, 1))
        offer_id = stock.offer.id

        # when
        with assert_no_duplicated_queries():
            response = TestClient(app.test_client()).get(f"/native/v1/offer/{offer_id}")

        # then
        assert response.status_code == 200
        assert response.json["stocks"][0]["activationCode"] is None

    @freeze_time("2020-01-01")
    def test_get_expired_offer(self, app):
        stock = offers_factories.EventStockFactory(beginningDatetime=datetime.utcnow() - timedelta(days=1))

        offer_id = stock.offer.id
        with assert_no_duplicated_queries():
            response = TestClient(app.test_client()).get(f"/native/v1/offer/{offer_id}")

        assert response.json["isExpired"]

    def test_get_offer_not_found(self, app):
        response = TestClient(app.test_client()).get("/native/v1/offer/1")

        assert response.status_code == 404

    @pytest.mark.parametrize(
        "validation", [OfferValidationStatus.DRAFT, OfferValidationStatus.PENDING, OfferValidationStatus.REJECTED]
    )
    def test_get_non_approved_offer(self, client, validation):
        offer = offers_factories.OfferFactory(validation=validation)

        with assert_no_duplicated_queries():
            response = client.get(f"/native/v1/offer/{offer.id}")
            assert response.status_code == 404

    @override_features(ENABLE_CDS_IMPLEMENTATION=True)
    @patch("pcapi.core.offers.api.external_bookings_api.get_shows_stock")
    def test_get_cds_synchonized_offer(self, mocked_get_shows_stock, app):
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
            idAtProviders=f"{offer_id_at_provider}#{show_id}/2022-12-03",
        )

        response = TestClient(app.test_client()).get(f"/native/v1/offer/{offer.id}")

        assert stock.remainingQuantity == 0
        assert response.json["stocks"][0]["isSoldOut"]

    @freeze_time("2023-01-01")
    @override_features(ENABLE_BOOST_API_INTEGRATION=True)
    @patch("pcapi.connectors.boost.requests.get")
    def test_get_boost_synchonized_offer(self, request_get, client):
        movie_id = 207
        first_show_id = 36683
        second_show_id = 36684

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
        second_show_stock = offers_factories.EventStockFactory(
            offer=offer, idAtProviders=f"{offer_id_at_provider}#{second_show_id}", quantity=96
        )

        response = client.get(f"/native/v1/offer/{offer.id}")
        assert response.status_code == 200
        assert first_show_stock.remainingQuantity == 96
        assert second_show_stock.remainingQuantity == 0

    @override_features(ENABLE_CGR_INTEGRATION=True)
    def test_get_cgr_synchronized_offer(self, requests_mock, app):
        allocine_movie_id = 234099
        first_show_id = 182021
        second_show_id = 182022

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
        first_show_stock = offers_factories.EventStockFactory(
            offer=offer, idAtProviders=f"{offer_id_at_provider}#{first_show_id}", quantity=95
        )
        second_show_stock = offers_factories.EventStockFactory(
            offer=offer, idAtProviders=f"{offer_id_at_provider}#{second_show_id}", quantity=95
        )

        response = TestClient(app.test_client()).get(f"/native/v1/offer/{offer.id}")

        assert response.status_code == 200
        assert first_show_stock.remainingQuantity == 95
        assert second_show_stock.remainingQuantity == 0

    @override_features(ENABLE_CDS_IMPLEMENTATION=True)
    def test_get_inactive_cinema_provider_offer(self, app):
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

        response = TestClient(app.test_client()).get(f"/native/v1/offer/{offer.id}")

        assert response.json["isReleased"] is False
        assert offer.isActive is False

    def should_have_metadata_describing_the_offer(self, client):
        offer = offers_factories.ThingOfferFactory()

        response = client.get(f"/native/v1/offer/{offer.id}")

        assert isinstance(response.json["metadata"], dict)
        assert response.json["metadata"]["@type"] == "Product"


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

        with assert_no_duplicated_queries():
            response = test_client.post("/native/v1/send_offer_webapp_link_by_email/98765432123456789")
            assert response.status_code == 404
        assert not mails_testing.outbox

    @pytest.mark.parametrize(
        "validation", [OfferValidationStatus.DRAFT, OfferValidationStatus.PENDING, OfferValidationStatus.REJECTED]
    )
    def test_send_non_approved_offer_webapp_link_by_email(self, app, validation):
        _, test_client = create_user_and_test_client(app)
        offer_id = offers_factories.OfferFactory(validation=validation).id

        with assert_no_duplicated_queries():
            response = test_client.post(f"/native/v1/send_offer_webapp_link_by_email/{offer_id}")
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
        offer = offers_factories.OfferFactory()
        offer_id = offer.id

        user, test_client = create_user_and_test_client(app)

        with assert_no_duplicated_queries():
            response = test_client.post(f"/native/v1/send_offer_link_by_push/{offer_id}")
            assert response.status_code == 204

        assert len(notifications_testing.requests) == 1

        notification = notifications_testing.requests[0]
        assert notification["user_ids"] == [user.id]

        assert offer.name in notification["message"]["title"]

    def test_send_offer_link_notification_not_found(self, app):
        """Test that no push notification is sent when offer is not found"""
        _, test_client = create_user_and_test_client(app)

        with assert_no_duplicated_queries():
            response = test_client.post("/native/v1/send_offer_link_by_push/9999999999")
            assert response.status_code == 404

        assert len(notifications_testing.requests) == 0

    @pytest.mark.parametrize(
        "validation", [OfferValidationStatus.DRAFT, OfferValidationStatus.PENDING, OfferValidationStatus.REJECTED]
    )
    def test_send_non_approved_offer_link_notification(self, app, validation):
        _, test_client = create_user_and_test_client(app)
        offer_id = offers_factories.OfferFactory(validation=validation).id

        with assert_no_duplicated_queries():
            response = test_client.post(f"/native/v1/send_offer_link_by_push/{offer_id}")
            assert response.status_code == 404

        assert len(notifications_testing.requests) == 0


class ReportOfferTest:
    def test_report_offer(self, app):
        user, test_client = create_user_and_test_client(app)
        offer = offers_factories.OfferFactory()

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
        offer = offers_factories.OfferFactory()

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
        offer = offers_factories.OfferFactory()

        offers_factories.OfferReportFactory(user=user, offer=offer)

        with assert_no_duplicated_queries():
            response = test_client.post(f"/native/v1/offer/{offer.id}/report", json={"reason": "PRICE_TOO_HIGH"})
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
    def test_report_non_approved_offer(self, app, validation):
        _, test_client = create_user_and_test_client(app)
        offer = offers_factories.ThingOfferFactory(validation=validation)

        response = test_client.post(f"/native/v1/offer/{offer.id}/report", json={"reason": "PRICE_TOO_HIGH"})

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

        assert set(response.json.keys()) == {
            "subcategories",
            "searchGroups",
            "homepageLabels",
            "nativeCategories",
            "genreTypes",
        }

        found_subcategory_ids = {x["id"] for x in response.json["subcategories"]}
        expected_subcategory_ids = {x.id for x in subcategories_v2.ALL_SUBCATEGORIES}
        assert found_subcategory_ids == expected_subcategory_ids

        found_search_group_names = {x["name"] for x in response.json["searchGroups"]}
        expected_search_group_names = {x.search_group_name for x in subcategories_v2.ALL_SUBCATEGORIES}
        assert found_search_group_names == expected_search_group_names

        found_home_labels = {x["name"] for x in response.json["homepageLabels"]}
        expected_home_labels = {x.homepage_label_name for x in subcategories_v2.ALL_SUBCATEGORIES}
        assert found_home_labels == expected_home_labels

        found_native_categories = {x["name"] for x in response.json["nativeCategories"]}
        expected_native_categories = {x.native_category.name for x in subcategories_v2.ALL_SUBCATEGORIES}
        assert found_native_categories == expected_native_categories

        found_genre_types = {x["name"] for x in response.json["genreTypes"]}
        expected_genre_types = {x.name for x in subcategories_v2.GenreType}
        assert found_genre_types == expected_genre_types
