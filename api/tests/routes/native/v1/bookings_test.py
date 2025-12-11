import hashlib
import hmac
import json
import re
from datetime import date
from datetime import datetime
from datetime import timedelta
from datetime import timezone
from decimal import Decimal
from unittest.mock import patch

import pytest
import time_machine
from pytest import approx

import pcapi.core.mails.testing as mails_testing
import pcapi.core.offers.factories as offers_factories
import pcapi.core.providers.factories as providers_factories
import pcapi.core.providers.repository as providers_api
import pcapi.notifications.push.testing as push_testing
from pcapi.core.bookings import factories as booking_factories
from pcapi.core.bookings import models as bookings_models
from pcapi.core.bookings.models import Booking
from pcapi.core.bookings.models import BookingCancellationReasons
from pcapi.core.bookings.models import BookingStatus
from pcapi.core.categories import subcategories
from pcapi.core.external_bookings.exceptions import ExternalBookingTimeoutException
from pcapi.core.external_bookings.factories import ExternalBookingFactory
from pcapi.core.finance import utils as finance_utils
from pcapi.core.geography.factories import AddressFactory
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offers import models as offer_models
from pcapi.core.offers.exceptions import UnexpectedCinemaProvider
from pcapi.core.providers import models as providers_models
from pcapi.core.providers.exceptions import InactiveProvider
from pcapi.core.providers.repository import get_provider_by_local_class
from pcapi.core.reactions.factories import ReactionFactory
from pcapi.core.reactions.models import ReactionTypeEnum
from pcapi.core.testing import assert_num_queries
from pcapi.core.users import factories as users_factories
from pcapi.models import db
from pcapi.models.validation_status_mixin import ValidationStatus
from pcapi.tasks.serialization.external_api_booking_notification_tasks import BookingAction
from pcapi.utils import date as date_utils
from pcapi.utils.human_ids import humanize

from tests.connectors.cgr import soap_definitions
from tests.local_providers.cinema_providers.cgr import fixtures as cgr_fixtures


pytestmark = pytest.mark.usefixtures("db_session")


class PostBookingTest:
    identifier = "pascal.ture@example.com"

    def test_post_bookings(self, client):
        yesterday = datetime.now(timezone.utc) - timedelta(days=1)
        stock = offers_factories.StockFactory(offer__bookingAllowedDatetime=yesterday)
        user = users_factories.BeneficiaryGrant18Factory(email=self.identifier)

        client = client.with_token(user)
        response = client.post("/native/v1/bookings", json={"stockId": stock.id, "quantity": 1})

        assert response.status_code == 200

        booking = db.session.query(Booking).filter(Booking.stockId == stock.id).first()
        assert booking.userId == user.id
        assert response.json["bookingId"] == booking.id
        assert booking.status == BookingStatus.CONFIRMED

    def test_no_stock_found(self, client):
        user = users_factories.BeneficiaryGrant18Factory(email=self.identifier)

        client = client.with_token(user)
        response = client.post("/native/v1/bookings", json={"stockId": 400, "quantity": 1})

        assert response.status_code == 400

    def test_insufficient_credit(self, client):
        user = users_factories.BeneficiaryGrant18Factory(email=self.identifier)
        stock = offers_factories.StockFactory(price=501)

        client = client.with_token(user)
        response = client.post("/native/v1/bookings", json={"stockId": stock.id, "quantity": 1})

        assert response.status_code == 400
        assert response.json["code"] == "INSUFFICIENT_CREDIT"

    def test_already_booked(self, client):
        user = users_factories.BeneficiaryGrant18Factory(email=self.identifier)
        booking = booking_factories.BookingFactory(user=user)

        client = client.with_token(user)
        response = client.post("/native/v1/bookings", json={"stockId": booking.stock.id, "quantity": 1})

        assert response.status_code == 400
        assert response.json["code"] == "ALREADY_BOOKED"

    def test_category_forbidden(self, client):
        stock = offers_factories.StockFactory(
            offer__subcategoryId=subcategories.VISITE_VIRTUELLE.id, offer__url="affreuse-offer.com"
        )
        user = users_factories.UnderageBeneficiaryFactory(email=self.identifier)

        client.with_token(user)

        response = client.post("/native/v1/bookings", json={"stockId": stock.id, "quantity": 1})

        assert response.status_code == 400
        assert response.json == {"code": "OFFER_CATEGORY_NOT_BOOKABLE_BY_USER"}

    @patch("pcapi.core.bookings.api.book_offer")
    def test_unexpected_offer_provider(self, mocked_book_offer, client):
        user = users_factories.BeneficiaryGrant18Factory(email=self.identifier)
        stock = offers_factories.EventStockFactory()
        mocked_book_offer.side_effect = InactiveProvider()

        client = client.with_token(user)
        response = client.post("/native/v1/bookings", json={"stockId": stock.id, "quantity": 1})

        assert response.status_code == 400
        assert response.json["code"] == "CINEMA_PROVIDER_INACTIVE"

    @patch("pcapi.core.bookings.api.book_offer")
    def test_inactive_provider(self, mocked_book_offer, client):
        user = users_factories.BeneficiaryGrant18Factory(email=self.identifier)
        stock = offers_factories.EventStockFactory()
        mocked_book_offer.side_effect = InactiveProvider()

        client = client.with_token(user)
        response = client.post("/native/v1/bookings", json={"stockId": stock.id, "quantity": 1})

        assert response.status_code == 400
        assert response.json["code"] == "CINEMA_PROVIDER_INACTIVE"

    @patch("pcapi.core.bookings.api.book_offer")
    def test_provider_timeout(self, mocked_book_offer, client):
        user = users_factories.BeneficiaryGrant18Factory(email=self.identifier)
        stock = offers_factories.EventStockFactory()
        mocked_book_offer.side_effect = ExternalBookingTimeoutException()

        client = client.with_token(user)
        response = client.post("/native/v1/bookings", json={"stockId": stock.id, "quantity": 1})

        assert response.status_code == 400
        assert response.json["code"] == "PROVIDER_BOOKING_TIMEOUT"

    @pytest.mark.parametrize(
        "subcategoryId,price",
        [(subcategoryId, 0) for subcategoryId in offer_models.Stock.AUTOMATICALLY_USED_SUBCATEGORIES],
    )
    def test_post_free_bookings_from_subcategories_with_archive(self, client, subcategoryId, price):
        stock = offers_factories.StockFactory(price=price, offer__subcategoryId=subcategoryId)
        user = users_factories.BeneficiaryGrant18Factory(email=self.identifier)

        client = client.with_token(user)
        response = client.post("/native/v1/bookings", json={"stockId": stock.id, "quantity": 1})

        assert response.status_code == 200

        booking = db.session.query(Booking).filter(Booking.stockId == stock.id).first()
        assert booking.userId == user.id
        assert response.json["bookingId"] == booking.id
        assert booking.status == BookingStatus.USED
        assert booking.dateUsed.strftime("%d/%m/%Y") == datetime.today().strftime("%d/%m/%Y")

    @pytest.mark.parametrize(
        "subcategory,price,status",
        [
            (subcategories.ABO_MEDIATHEQUE, 10, BookingStatus.CONFIRMED),
            (subcategories.ACTIVATION_THING, 0, BookingStatus.CONFIRMED),
        ],
    )
    def test_post_non_free_bookings_or_from_wrong_subcategories_without_archive(
        self, client, subcategory, price, status
    ):
        stock = offers_factories.StockFactory(price=price, offer__subcategoryId=subcategory.id)
        user = users_factories.BeneficiaryGrant18Factory(email=self.identifier)

        client = client.with_token(user)
        response = client.post("/native/v1/bookings", json={"stockId": stock.id, "quantity": 1})

        assert response.status_code == 200

        booking = db.session.query(Booking).filter(Booking.stockId == stock.id).first()
        assert booking.userId == user.id
        assert response.json["bookingId"] == booking.id
        assert booking.status == BookingStatus.CONFIRMED
        assert not booking.dateUsed

    @patch("pcapi.tasks.external_api_booking_notification_tasks.external_api_booking_notification_task.delay")
    def test_bookings_send_notification_to_external_api_with_external_event_booking(self, mocked_task, client):
        base_url = "https://book_my_offer.com"
        external_notification_url = base_url + "/notify"

        eighteen_years_ago = datetime(date.today().year - 18, 1, 1)
        user = users_factories.BeneficiaryGrant18Factory(
            email=self.identifier, dateOfBirth=eighteen_years_ago, phoneNumber="+33101010101"
        )
        provider = providers_factories.ProviderFactory(
            name="Technical provider",
            localClass=None,
            notificationExternalUrl=external_notification_url,
        )
        providers_factories.OffererProviderFactory(provider=provider)
        stock = offers_factories.EventStockFactory(
            lastProvider=provider,
            priceCategory__price=2,
            offer__subcategoryId=subcategories.SEANCE_ESSAI_PRATIQUE_ART.id,
            offer__lastProvider=provider,
            offer__ean="1234567890123",
            idAtProviders="",
            dnBookedQuantity=14,
            quantity=20,
        )

        response = client.with_token(user).post(
            "/native/v1/bookings",
            json={"stockId": stock.id, "quantity": 1},
        )

        assert response.status_code == 200

        booking = db.session.query(Booking).filter(Booking.stockId == stock.id).first()
        assert booking.userId == user.id
        assert response.json["bookingId"] == booking.id
        assert booking.status == BookingStatus.CONFIRMED
        assert not booking.dateUsed

        assert mocked_task.call_count == 1
        notification = mocked_task.call_args.args[0].data
        assert notification.offer_ean == "1234567890123"
        assert notification.offer_id == stock.offer.id
        assert notification.offer_name == stock.offer.name
        assert notification.offer_price == 200
        assert notification.stock_id == stock.id
        assert notification.booking_quantity == booking.quantity
        assert notification.booking_creation_date == booking.dateCreated
        assert notification.venue_address == stock.offer.venue.offererAddress.address.street
        assert notification.user_email == user.email
        assert notification.user_first_name == user.firstName
        assert notification.user_last_name == user.lastName
        assert notification.user_phone == user.phoneNumber
        assert notification.action == BookingAction.BOOK

        assert mocked_task.call_args.args[0].notificationUrl == external_notification_url

    def test_bookings_with_external_event_booking_infos(self, client, requests_mock):
        external_booking_url = "https://book_my_offer.com/confirm"

        eighteen_years_ago = datetime(date.today().year - 18, 1, 1)
        user = users_factories.BeneficiaryGrant18Factory(
            email=self.identifier, dateOfBirth=eighteen_years_ago, phoneNumber="+33101010101"
        )
        provider = providers_factories.ProviderFactory(
            name="Technical provider",
            localClass=None,
            bookingExternalUrl=external_booking_url,
            cancelExternalUrl=external_booking_url,
        )
        providers_factories.OffererProviderFactory(provider=provider)
        stock = offers_factories.EventStockFactory(
            lastProvider=provider,
            priceCategory__price=2,
            offer__subcategoryId=subcategories.SEANCE_ESSAI_PRATIQUE_ART.id,
            offer__lastProvider=provider,
            offer__withdrawalType=offer_models.WithdrawalTypeEnum.IN_APP,
            offer__ean="1234567890123",
            idAtProviders="",
            dnBookedQuantity=14,
            quantity=20,
        )

        requests_mock.post(
            external_booking_url,
            json={"tickets": [{"barcode": "12123932898127", "seat": "A12"}], "remainingQuantity": 50},
            status_code=201,
        )

        response = client.with_token(user).post(
            "/native/v1/bookings",
            json={"stockId": stock.id, "quantity": 1},
        )

        assert response.status_code == 200

        json_data = json.loads(requests_mock.last_request.json())

        assert (
            requests_mock.last_request.headers["PassCulture-Signature"]
            == hmac.new(provider.hmacKey.encode(), json.dumps(json_data).encode(), hashlib.sha256).hexdigest()
        )

        now = date_utils.get_naive_utc_now()
        json_confirmation_date = datetime.fromisoformat(json_data.pop("booking_confirmation_date"))
        json_creation_date = datetime.fromisoformat(json_data.pop("booking_creation_date"))

        assert json_confirmation_date.timestamp() == approx(now.timestamp(), rel=1)
        assert json_creation_date.timestamp() == approx(now.timestamp(), rel=1)

        assert json_data == {
            "booking_quantity": 1,
            "offer_ean": "1234567890123",
            "offer_id": stock.offer.id,
            "offer_id_at_provider": stock.offer.idAtProvider,
            "offer_name": stock.offer.name,
            "offer_price": finance_utils.to_cents(stock.priceCategory.price),
            "price_category_id": stock.priceCategoryId,
            "price_category_id_at_provider": stock.priceCategory.idAtProvider,
            "price_category_label": stock.priceCategory.label,
            "stock_id": stock.id,
            "stock_id_at_provider": "",
            "user_birth_date": f"{eighteen_years_ago.year}-01-01",
            "user_email": user.email,
            "user_first_name": user.firstName,
            "user_last_name": user.lastName,
            "user_phone": user.phoneNumber,
            "venue_address": stock.offer.venue.offererAddress.address.street,
            "venue_department_code": stock.offer.venue.offererAddress.address.departmentCode,
            "venue_id": stock.offer.venue.id,
            "venue_name": stock.offer.venue.name,
        }
        external_bookings = db.session.query(bookings_models.ExternalBooking).one()
        assert external_bookings.bookingId == response.json["bookingId"]
        assert external_bookings.barcode == "12123932898127"
        assert external_bookings.seat == "A12"
        assert stock.quantity == 50 + 15  # remainingQuantity + dnBookedQuantity after new booking
        assert stock.dnBookedQuantity == 15

    def test_bookings_with_external_event_booking_and_remaining_quantity_unlimited(self, client, requests_mock):
        external_booking_url = "https://book_my_offer.com/confirm"
        eighteen_years_ago = datetime(date.today().year - 18, 1, 1)
        user = users_factories.BeneficiaryGrant18Factory(
            email=self.identifier, dateOfBirth=eighteen_years_ago, phoneNumber="+33101010101"
        )
        provider = providers_factories.ProviderFactory(
            name="Technical provider",
            localClass=None,
            bookingExternalUrl=external_booking_url,
            cancelExternalUrl=external_booking_url,
        )
        providers_factories.OffererProviderFactory(provider=provider)
        stock = offers_factories.EventStockFactory(
            lastProvider=provider,
            priceCategory__price=2,
            offer__subcategoryId=subcategories.SEANCE_ESSAI_PRATIQUE_ART.id,
            offer__lastProvider=provider,
            offer__withdrawalType=offer_models.WithdrawalTypeEnum.IN_APP,
            offer__ean="1234567890123",
            idAtProviders="",
            dnBookedQuantity=14,
            quantity=20,
        )

        requests_mock.post(
            external_booking_url,
            json={"tickets": [{"barcode": "12123932898127", "seat": "A12"}], "remainingQuantity": None},
            status_code=201,
        )

        response = client.with_token(user).post(
            "/native/v1/bookings",
            json={"stockId": stock.id, "quantity": 1},
        )

        assert response.status_code == 200
        json_data = json.loads(requests_mock.last_request.json())

        now = date_utils.get_naive_utc_now()
        json_confirmation_date = datetime.fromisoformat(json_data.pop("booking_confirmation_date"))
        json_creation_date = datetime.fromisoformat(json_data.pop("booking_creation_date"))

        assert json_confirmation_date.timestamp() == approx(now.timestamp(), rel=1)
        assert json_creation_date.timestamp() == approx(now.timestamp(), rel=1)

        assert json_data == {
            "booking_quantity": 1,
            "offer_ean": "1234567890123",
            "offer_id": stock.offer.id,
            "offer_id_at_provider": stock.offer.idAtProvider,
            "offer_name": stock.offer.name,
            "offer_price": finance_utils.to_cents(stock.priceCategory.price),
            "price_category_id": stock.priceCategoryId,
            "price_category_id_at_provider": stock.priceCategory.idAtProvider,
            "price_category_label": stock.priceCategory.label,
            "stock_id": stock.id,
            "stock_id_at_provider": "",
            "user_birth_date": eighteen_years_ago.strftime("%Y-%m-%d"),
            "user_email": user.email,
            "user_first_name": user.firstName,
            "user_last_name": user.lastName,
            "user_phone": user.phoneNumber,
            "venue_address": stock.offer.venue.offererAddress.address.street,
            "venue_department_code": stock.offer.venue.offererAddress.address.departmentCode,
            "venue_id": stock.offer.venue.id,
            "venue_name": stock.offer.venue.name,
        }
        external_bookings = db.session.query(bookings_models.ExternalBooking).one()
        assert external_bookings.bookingId == response.json["bookingId"]
        assert external_bookings.barcode == "12123932898127"
        assert external_bookings.seat == "A12"
        assert stock.quantity == None  # stock quantity is unlimited the value is None in the database
        assert stock.remainingQuantity == "unlimited"
        assert stock.dnBookedQuantity == 15

    @time_machine.travel("2022-10-12 17:09:25")
    def test_bookings_with_external_event_booking_sold_out(self, client, requests_mock):
        external_booking_url = "https://book_my_offer.com/confirm"
        user = users_factories.BeneficiaryGrant18Factory(
            email=self.identifier, dateOfBirth=datetime(2007, 1, 1), phoneNumber="+33101010101"
        )
        provider = providers_factories.ProviderFactory(
            name="Technical provider",
            localClass=None,
            bookingExternalUrl=external_booking_url,
            cancelExternalUrl=external_booking_url,
        )
        providers_factories.OffererProviderFactory(provider=provider)
        stock = offers_factories.EventStockFactory(
            lastProvider=provider,
            offer__subcategoryId=subcategories.SEANCE_ESSAI_PRATIQUE_ART.id,
            offer__lastProvider=provider,
            offer__withdrawalType=offer_models.WithdrawalTypeEnum.IN_APP,
            idAtProviders="",
            quantity=25,
            dnBookedQuantity=10,
        )

        requests_mock.post(external_booking_url, json={"error": "sold_out", "remainingQuantity": 0}, status_code=409)

        response = client.with_token(user).post("/native/v1/bookings", json={"stockId": stock.id, "quantity": 1})

        assert response.status_code == 400
        assert response.json == {"code": "PROVIDER_STOCK_NOT_ENOUGH_SEATS"}
        assert stock.quantity == 10
        assert len(db.session.query(bookings_models.ExternalBooking).all()) == 0
        assert len(db.session.query(bookings_models.Booking).all()) == 0

    @time_machine.travel("2022-10-12 17:09:25")
    def test_book_sold_out_cinema_stock_does_not_book_anything(self, client, requests_mock):
        user = users_factories.BeneficiaryGrant18Factory(email=self.identifier, dateOfBirth=datetime(2007, 1, 1))
        requests_mock.get("http://example.com/web_service?wsdl", text=soap_definitions.WEB_SERVICE_DEFINITION)
        id_at_provider = "test_id_at_provider"

        provider = db.session.query(providers_models.Provider).filter_by(localClass="CGRStocks").first()
        venue_provider = providers_factories.VenueProviderFactory(
            provider=provider, venueIdAtOfferProvider=id_at_provider
        )
        pivot = providers_factories.CinemaProviderPivotFactory(
            venue=venue_provider.venue, provider=provider, idAtProvider=id_at_provider
        )
        providers_factories.CGRCinemaDetailsFactory(
            cinemaProviderPivot=pivot,
            cinemaUrl="http://example.com/web_service",
        )

        providers_factories.OffererProviderFactory(provider=provider)
        stock = offers_factories.EventStockFactory(
            lastProvider=provider,
            offer__subcategoryId=subcategories.SEANCE_CINE.id,
            offer__lastProvider=provider,
            offer__withdrawalType=offer_models.WithdrawalTypeEnum.IN_APP,
            offer__venue=venue_provider.venue,
            quantity=1,
            idAtProviders="#1",
        )

        with patch("pcapi.core.providers.clients.cgr_client.CGRAPIClient.book_ticket") as mock_book_ticket:
            mock_book_ticket.side_effect = RuntimeError("test")

            response = client.with_token(user).post("/native/v1/bookings", json={"stockId": stock.id, "quantity": 1})

        assert response.status_code == 400
        assert response.json == {"code": "CINEMA_PROVIDER_BOOKING_FAILED"}
        assert stock.quantity == 1

    @time_machine.travel("2022-10-12 17:09:25")
    def test_bookings_with_external_event_booking_not_enough_quantity(self, client, requests_mock):
        external_booking_url = "https://book_my_offer.com/confirm"
        user = users_factories.BeneficiaryGrant18Factory(
            email=self.identifier, dateOfBirth=datetime(2007, 1, 1), phoneNumber="+33101010101", deposit__amount=500
        )
        provider = providers_factories.ProviderFactory(
            name="Technical provider",
            localClass=None,
            bookingExternalUrl=external_booking_url,
            cancelExternalUrl=external_booking_url,
        )
        providers_factories.OffererProviderFactory(provider=provider)
        stock = offers_factories.EventStockFactory(
            lastProvider=provider,
            offer__subcategoryId=subcategories.SEANCE_ESSAI_PRATIQUE_ART.id,
            offer__lastProvider=provider,
            offer__withdrawalType=offer_models.WithdrawalTypeEnum.IN_APP,
            offer__isDuo=True,
            idAtProviders="",
            quantity=25,
            dnBookedQuantity=10,
        )

        requests_mock.post(
            external_booking_url, json={"error": "not_enough_seats", "remainingQuantity": 1}, status_code=409
        )

        response = client.with_token(user).post("/native/v1/bookings", json={"stockId": stock.id, "quantity": 2})

        assert response.status_code == 400
        assert response.json == {"code": "PROVIDER_STOCK_NOT_ENOUGH_SEATS"}
        assert stock.quantity == 11
        assert len(db.session.query(bookings_models.ExternalBooking).all()) == 0
        assert len(db.session.query(bookings_models.Booking).all()) == 0

    @time_machine.travel("2022-10-12 17:09:25")
    def test_bookings_with_external_event_booking_when_response_fields_are_too_long(self, client, requests_mock):
        external_booking_url = "https://book_my_offer.com/confirm"
        user = users_factories.BeneficiaryGrant18Factory(email=self.identifier)
        provider = providers_factories.ProviderFactory(
            bookingExternalUrl=external_booking_url,
            cancelExternalUrl=external_booking_url,
        )
        providers_factories.OffererProviderFactory(provider=provider)
        stock = offers_factories.EventStockFactory(
            lastProvider=provider,
            offer__lastProvider=provider,
            offer__withdrawalType=offer_models.WithdrawalTypeEnum.IN_APP,
            idAtProviders="",
        )

        barcode = "1" * 101
        seat = "A" * 151

        requests_mock.post(
            external_booking_url,
            json={"tickets": [{"barcode": barcode, "seat": seat}], "remainingQuantity": 50},
            status_code=201,
        )

        response = client.with_token(user).post(
            "/native/v1/bookings",
            json={"stockId": stock.id, "quantity": 1},
        )

        assert response.status_code == 400
        assert response.json == {
            "code": "EXTERNAL_EVENT_PROVIDER_BOOKING_FAILED",
            "message": "External booking failed.",
        }

    @pytest.mark.features(ENABLE_EMS_INTEGRATION=True)
    @pytest.mark.parametrize(
        "error_payload",
        [
            {"statut": 0, "code_erreur": 104, "message_erreur": "Il n'y a plus de séance disponible pour ce film"},
            {"statut": 0, "code_erreur": 106, "message_erreur": "La séance n'est plus disponible à la vente"},
        ],
    )
    def test_handle_ems_showtime_fully_booked_cases(self, error_payload, client, requests_mock):
        user = users_factories.BeneficiaryGrant18Factory(email=self.identifier)
        ems_provider = get_provider_by_local_class("EMSStocks")
        venue_provider = providers_factories.VenueProviderFactory(provider=ems_provider)
        cinema_provider_pivot = providers_factories.CinemaProviderPivotFactory(venue=venue_provider.venue)
        offer = offers_factories.EventOfferFactory(
            name="Film",
            venue=venue_provider.venue,
            subcategoryId=subcategories.SEANCE_CINE.id,
            lastProviderId=cinema_provider_pivot.provider.id,
        )
        stock = offers_factories.EventStockFactory(offer=offer, idAtProviders="1111%2222%EMS#3333")

        requests_mock.post(
            url=re.compile(r"https://fake_url.com/VENTE/*"),
            json=error_payload,
        )

        response = client.with_token(user).post(
            "/native/v1/bookings",
            json={"stockId": stock.id, "quantity": 1},
        )

        assert response.status_code == 400
        assert response.json["code"] == "PROVIDER_STOCK_NOT_ENOUGH_SEATS"

    @pytest.mark.features(ENABLE_EMS_INTEGRATION=True)
    def test_handle_ems_showtime_does_not_exist_case(self, client, requests_mock):
        user = users_factories.BeneficiaryGrant18Factory(email=self.identifier)
        ems_provider = get_provider_by_local_class("EMSStocks")
        venue_provider = providers_factories.VenueProviderFactory(provider=ems_provider)
        cinema_provider_pivot = providers_factories.CinemaProviderPivotFactory(venue=venue_provider.venue)
        offer = offers_factories.EventOfferFactory(
            name="Film",
            venue=venue_provider.venue,
            subcategoryId=subcategories.SEANCE_CINE.id,
            lastProviderId=cinema_provider_pivot.provider.id,
        )
        stock = offers_factories.EventStockFactory(offer=offer, idAtProviders="1111%2222%EMS#3333")

        requests_mock.post(
            url=re.compile(r"https://fake_url.com/VENTE/*"),
            json={"statut": 0, "code_erreur": 105, "message_erreur": "La séance n'a pas été trouvée"},
        )

        response = client.with_token(user).post(
            "/native/v1/bookings",
            json={"stockId": stock.id, "quantity": 1},
        )

        assert response.status_code == 400
        assert response.json["code"] == "PROVIDER_SHOW_DOES_NOT_EXIST"
        assert stock.isSoftDeleted
        assert len(db.session.query(bookings_models.Booking).all()) == 0

    @time_machine.travel("2022-10-12 17:09:25")
    @pytest.mark.parametrize(
        "error_message",
        [
            "Séance inconnue.",
            "PASS CULTURE IMPOSSIBLE erreur création résa (site) : IdSeance(528581) inconnu",
        ],
    )
    def test_handle_cgr_showtime_does_not_exist_case(self, error_message, client, requests_mock):
        user = users_factories.BeneficiaryGrant18Factory(email=self.identifier, dateOfBirth=datetime(2007, 1, 1))
        requests_mock.get("http://example.com/web_service?wsdl", text=soap_definitions.WEB_SERVICE_DEFINITION)
        requests_mock.post(
            "http://example.com/web_service",
            text=cgr_fixtures.cgr_reservation_error_response_template(
                99,  # not sure this is the actual error code for this error
                error_message,
            ),
        )
        id_at_provider = "test_id_at_provider"

        provider = db.session.query(providers_models.Provider).filter_by(localClass="CGRStocks").first()
        venue_provider = providers_factories.VenueProviderFactory(
            provider=provider, venueIdAtOfferProvider=id_at_provider
        )
        pivot = providers_factories.CinemaProviderPivotFactory(
            venue=venue_provider.venue, provider=provider, idAtProvider=id_at_provider
        )
        providers_factories.CGRCinemaDetailsFactory(
            cinemaProviderPivot=pivot,
            cinemaUrl="http://example.com/web_service",
        )

        providers_factories.OffererProviderFactory(provider=provider)
        stock = offers_factories.EventStockFactory(
            lastProvider=provider,
            offer__subcategoryId=subcategories.SEANCE_CINE.id,
            offer__lastProvider=provider,
            offer__withdrawalType=offer_models.WithdrawalTypeEnum.IN_APP,
            offer__venue=venue_provider.venue,
            quantity=1,
            idAtProviders="#1",
        )

        response = client.with_token(user).post("/native/v1/bookings", json={"stockId": stock.id, "quantity": 1})

        assert response.status_code == 400
        assert response.json == {"code": "PROVIDER_SHOW_DOES_NOT_EXIST"}
        assert stock.isSoftDeleted
        assert len(db.session.query(bookings_models.Booking).all()) == 0

    @time_machine.travel("2022-10-12 17:09:25")
    def test_handle_boost_showtime_does_not_exist_case(self, client, requests_mock):
        user = users_factories.BeneficiaryGrant18Factory(email=self.identifier, dateOfBirth=datetime(2007, 1, 1))

        id_at_provider = "test_id_at_provider"

        provider = db.session.query(providers_models.Provider).filter_by(localClass="BoostStocks").first()
        venue_provider = providers_factories.VenueProviderFactory(
            provider=provider, venueIdAtOfferProvider=id_at_provider
        )
        pivot = providers_factories.CinemaProviderPivotFactory(
            venue=venue_provider.venue, provider=provider, idAtProvider=id_at_provider
        )
        providers_factories.BoostCinemaDetailsFactory(
            cinemaUrl="https://cinema-0.example.com/", cinemaProviderPivot=pivot
        )

        providers_factories.OffererProviderFactory(provider=provider)
        stock = offers_factories.EventStockFactory(
            lastProvider=provider,
            offer__subcategoryId=subcategories.SEANCE_CINE.id,
            offer__lastProvider=provider,
            offer__withdrawalType=offer_models.WithdrawalTypeEnum.IN_APP,
            offer__venue=venue_provider.venue,
            quantity=1,
            idAtProviders="#1",
        )
        requests_mock.get(
            "https://cinema-0.example.com/api/showtimes/1",
            status_code=400,
            json={"code": 400, "message": "No showtime found"},
        )
        post_adapter = requests_mock.post("https://cinema-0.example.com/api/sale/complete")

        response = client.with_token(user).post("/native/v1/bookings", json={"stockId": stock.id, "quantity": 1})

        assert response.status_code == 400
        assert response.json == {"code": "PROVIDER_SHOW_DOES_NOT_EXIST"}
        assert stock.isSoftDeleted
        assert len(db.session.query(bookings_models.Booking).all()) == 0
        assert post_adapter.last_request == None

    @time_machine.travel("2022-10-12 17:09:25")
    @pytest.mark.settings(CDS_API_URL="apiUrl_test/")
    def test_handle_cds_showtime_does_not_exist_case(
        self,
        client,
        requests_mock,
    ):
        user = users_factories.BeneficiaryGrant18Factory(email=self.identifier, dateOfBirth=datetime(2007, 1, 1))

        id_at_provider = "test_id_at_provider"

        provider = db.session.query(providers_models.Provider).filter_by(localClass="CDSStocks").first()
        venue_provider = providers_factories.VenueProviderFactory(
            provider=provider, venueIdAtOfferProvider=id_at_provider
        )
        pivot = providers_factories.CinemaProviderPivotFactory(
            venue=venue_provider.venue, provider=provider, idAtProvider=id_at_provider
        )
        providers_factories.CDSCinemaDetailsFactory(
            accountId="accountid_test",
            cinemaProviderPivot=pivot,
            cinemaApiToken="token_test",
        )
        stock = offers_factories.EventStockFactory(
            lastProvider=provider,
            offer__subcategoryId=subcategories.SEANCE_CINE.id,
            offer__lastProvider=provider,
            offer__withdrawalType=offer_models.WithdrawalTypeEnum.IN_APP,
            offer__venue=venue_provider.venue,
            quantity=1,
            idAtProviders="#1",
        )
        requests_mock.get(
            "https://accountid_test.apiUrl_test/shows",
            status_code=200,
            json=[
                {
                    "id": 123456,  # id does not match
                    "remaining_place": 88,
                    "internet_remaining_place": 10,
                    "disableseatmap": False,
                    "is_empty_seatmap": False,
                    "showtime": "2022-03-28T12:00:00.000+0200",
                    "is_cancelled": False,
                    "is_deleted": False,
                    "showsTariffPostypeCollection": [{"tariffid": {"id": 96}}],
                    "screenid": {"id": 10},
                    "mediaid": {"id": 52},
                    "showsMediaoptionsCollection": [
                        {"mediaoptionsid": {"id": 12}},
                    ],
                },
            ],
        )

        post_adapter = requests_mock.post(
            "https://accountid_test.apiUrl_test/transaction/create?api_token=token_test",
            json={},
        )

        response = client.with_token(user).post("/native/v1/bookings", json={"stockId": stock.id, "quantity": 1})

        assert response.status_code == 400
        assert response.json == {"code": "PROVIDER_SHOW_DOES_NOT_EXIST"}
        assert stock.isSoftDeleted
        assert len(db.session.query(bookings_models.Booking).all()) == 0
        assert post_adapter.last_request == None

    @time_machine.travel("2022-10-12 17:09:25")
    def test_bookings_with_external_event_api_return_less_tickets_than_quantity(self, client, requests_mock):
        external_booking_url = "https://book_my_offer.com/confirm"
        cancel_booking_url = "https://book_my_offer.com/cancel"
        user = users_factories.BeneficiaryGrant18Factory(
            email=self.identifier, dateOfBirth=datetime(2007, 1, 1), phoneNumber="+33101010101", deposit__amount=500
        )
        provider = providers_factories.ProviderFactory(
            name="Technical provider",
            localClass=None,
            bookingExternalUrl=external_booking_url,
            cancelExternalUrl=cancel_booking_url,
        )
        providers_factories.OffererProviderFactory(provider=provider)
        stock = offers_factories.EventStockFactory(
            lastProvider=provider,
            offer__subcategoryId=subcategories.SEANCE_ESSAI_PRATIQUE_ART.id,
            offer__lastProvider=provider,
            offer__withdrawalType=offer_models.WithdrawalTypeEnum.IN_APP,
            offer__isDuo=True,
            dnBookedQuantity=12,
            quantity=15,
            idAtProviders="",
        )

        requests_mock.post(
            external_booking_url,
            json={"tickets": [{"barcode": "12123932898127", "seat": "A12"}], "remainingQuantity": 100},
            status_code=201,
        )

        requests_mock.post(
            cancel_booking_url,
            json={"remainingQuantity": 50},
            status_code=200,
        )

        response = client.with_token(user).post("/native/v1/bookings", json={"stockId": stock.id, "quantity": 2})

        assert response.status_code == 400
        assert response.json == {
            "code": "EXTERNAL_EVENT_PROVIDER_BOOKING_FAILED",
            "message": "External booking failed with status code 201 but only one ticket "
            "was returned for duo reservation",
        }
        assert stock.quantity == 15
        assert len(db.session.query(bookings_models.ExternalBooking).all()) == 0
        assert len(db.session.query(bookings_models.Booking).all()) == 0

    @time_machine.travel("2022-10-12 17:09:25")
    def test_bookings_with_external_event_api_return_nothing(self, client, requests_mock):
        external_booking_url = "https://book_my_offer.com/confirm"
        cancel_booking_url = "https://book_my_offer.com/cancel"
        user = users_factories.BeneficiaryGrant18Factory(
            email=self.identifier, dateOfBirth=datetime(2007, 1, 1), phoneNumber="+33101010101", deposit__amount=500
        )
        provider = providers_factories.ProviderFactory(
            name="Technical provider",
            localClass=None,
            bookingExternalUrl=external_booking_url,
            cancelExternalUrl=cancel_booking_url,
        )
        providers_factories.OffererProviderFactory(provider=provider)
        stock = offers_factories.EventStockFactory(
            lastProvider=provider,
            offer__lastProvider=provider,
            offer__withdrawalType=offer_models.WithdrawalTypeEnum.IN_APP,
            idAtProviders="",
        )

        requests_mock.post(
            external_booking_url,
            json=None,
            status_code=201,
        )

        response = client.with_token(user).post("/native/v1/bookings", json={"stockId": stock.id, "quantity": 1})

        assert response.status_code == 400
        assert response.json == {
            "code": "EXTERNAL_EVENT_PROVIDER_BOOKING_FAILED",
            "message": "External booking failed.",
        }
        assert len(db.session.query(bookings_models.ExternalBooking).all()) == 0
        assert len(db.session.query(bookings_models.Booking).all()) == 0

    def test_bookings_with_external_event_api_return_more_tickets_than_quantity(self, client, requests_mock):
        external_booking_url = "https://book_my_offer.com/confirm"
        cancel_booking_url = "https://book_my_offer.com/cancel"
        eighteen_years_ago = datetime(date.today().year - 18, 1, 1)
        user = users_factories.BeneficiaryGrant18Factory(
            email=self.identifier, dateOfBirth=eighteen_years_ago, phoneNumber="+33101010101", deposit__amount=500
        )
        provider = providers_factories.ProviderFactory(
            name="Technical provider",
            localClass=None,
            bookingExternalUrl=external_booking_url,
            cancelExternalUrl=cancel_booking_url,
        )
        providers_factories.OffererProviderFactory(provider=provider)
        stock = offers_factories.EventStockFactory(
            lastProvider=provider,
            offer__subcategoryId=subcategories.SEANCE_ESSAI_PRATIQUE_ART.id,
            offer__lastProvider=provider,
            offer__withdrawalType=offer_models.WithdrawalTypeEnum.IN_APP,
            dnBookedQuantity=10,
            idAtProviders="",
        )

        requests_mock.post(
            external_booking_url,
            json={
                "tickets": [{"barcode": "12123932898127", "seat": "A12"}, {"barcode": "12123932898117", "seat": "A13"}],
                "remainingQuantity": 50,
            },
            status_code=201,
        )

        requests_mock.post(
            cancel_booking_url,
            json={"remainingQuantity": 50},
            status_code=200,
        )

        response = client.with_token(user).post("/native/v1/bookings", json={"stockId": stock.id, "quantity": 1})

        assert response.status_code == 200
        external_booking = db.session.query(bookings_models.ExternalBooking).one()
        assert external_booking.bookingId == response.json["bookingId"]
        assert stock.quantity == 50 + 11  # remainingQuantity + dnBookedQuantity after new booking
        assert stock.dnBookedQuantity == 11

        assert external_booking.barcode in ["12123932898127", "12123932898117"]
        assert external_booking.seat in ["A12", "A13"]

    @pytest.mark.parametrize(
        "validation_status",
        [ValidationStatus.NEW, ValidationStatus.PENDING, ValidationStatus.REJECTED, ValidationStatus.CLOSED],
    )
    def test_offerer_not_validated(self, client, validation_status):
        stock = offers_factories.StockFactory(offer__venue__managingOfferer__validationStatus=validation_status)
        user = users_factories.BeneficiaryGrant18Factory(email=self.identifier)

        client = client.with_token(user)
        response = client.post("/native/v1/bookings", json={"stockId": stock.id, "quantity": 1})

        assert response.status_code == 400
        assert response.json == {"code": "STOCK_NOT_BOOKABLE"}
        assert db.session.query(Booking).count() == 0

    def test_offer_cannot_be_booked_if_not_bookable_yet(self, client):
        later = datetime.now(timezone.utc) + timedelta(days=64)
        stock = offers_factories.StockFactory(offer__bookingAllowedDatetime=later)
        user = users_factories.BeneficiaryGrant18Factory(email=self.identifier)

        client = client.with_token(user)
        response = client.post("/native/v1/bookings", json={"stockId": stock.id, "quantity": 1})

        assert response.status_code == 400
        assert response.json == {"code": "STOCK_NOT_BOOKABLE"}
        assert db.session.query(Booking).count() == 0

    def test_offer_without_allowed_booking_dt_set_can_be_booked(self, client):
        stock = offers_factories.StockFactory(offer__bookingAllowedDatetime=None)
        user = users_factories.BeneficiaryGrant18Factory(email=self.identifier)

        client = client.with_token(user)
        response = client.post("/native/v1/bookings", json={"stockId": stock.id, "quantity": 1})

        assert response.status_code == 200

        booking = db.session.query(Booking).filter(Booking.stockId == stock.id).first()
        assert booking.userId == user.id
        assert response.json["bookingId"] == booking.id
        assert booking.status == BookingStatus.CONFIRMED


class GetBookingsTest:
    identifier = "pascal.ture@example.com"

    def test_get_bookings(self, client):
        OFFER_URL = "https://demo.pass/some/path?token={token}&email={email}&offerId={offerId}"
        user = users_factories.BeneficiaryFactory(email=self.identifier, age=18)

        permanent_booking = booking_factories.UsedBookingFactory(
            user=user,
            stock__offer__subcategoryId=subcategories.TELECHARGEMENT_LIVRE_AUDIO.id,
            dateUsed=datetime(2023, 2, 3),
        )

        event_booking = booking_factories.BookingFactory(
            user=user,
            stock=offers_factories.EventStockFactory(
                beginningDatetime=date_utils.get_naive_utc_now() + timedelta(days=2),
                offer__bookingContact="contact@example.net",
            ),
        )

        digital_stock = offers_factories.StockWithActivationCodesFactory()
        first_activation_code = digital_stock.activationCodes[0]
        second_activation_code = digital_stock.activationCodes[1]
        digital_booking = booking_factories.UsedBookingFactory(
            user=user,
            stock=digital_stock,
            activationCode=first_activation_code,
        )
        ended_digital_booking = booking_factories.UsedBookingFactory(
            user=user,
            displayAsEnded=True,
            stock=digital_stock,
            activationCode=second_activation_code,
        )
        expire_tomorrow = booking_factories.BookingFactory(
            user=user, dateCreated=date_utils.get_naive_utc_now() - timedelta(days=29)
        )
        used_but_in_future = booking_factories.UsedBookingFactory(
            user=user,
            dateUsed=date_utils.get_naive_utc_now() - timedelta(days=1),
            stock=offers_factories.StockFactory(beginningDatetime=date_utils.get_naive_utc_now() + timedelta(days=3)),
        )

        cancelled_permanent_booking = booking_factories.CancelledBookingFactory(
            user=user,
            stock__offer__subcategoryId=subcategories.TELECHARGEMENT_LIVRE_AUDIO.id,
            cancellation_date=datetime(2023, 3, 10),
        )
        cancelled = booking_factories.CancelledBookingFactory(user=user, cancellation_date=datetime(2023, 3, 8))
        used1 = booking_factories.UsedBookingFactory(user=user, dateUsed=datetime(2023, 3, 1))
        used2 = booking_factories.UsedBookingFactory(
            user=user,
            displayAsEnded=True,
            dateUsed=datetime(2023, 3, 2),
            stock__offer__url=OFFER_URL,
            stock__offer__subcategoryId=subcategories.ABO_LIVRE_NUMERIQUE.id,
            stock__features=["VO"],
            stock__offer__extraData=None,
            cancellation_limit_date=datetime(2023, 3, 2),
        )

        mediation = offers_factories.MediationFactory(
            id=111, offer=used2.stock.offer, thumbCount=1, credit="street credit"
        )

        client = client.with_token(user)
        with assert_num_queries(2):
            # select user, booking
            response = client.get("/native/v1/bookings")

        assert response.status_code == 200

        assert [b["id"] for b in response.json["ongoing_bookings"]] == [
            expire_tomorrow.id,
            event_booking.id,
            used_but_in_future.id,
            digital_booking.id,
            permanent_booking.id,
        ]

        event_booking_json = next(
            booking for booking in response.json["ongoing_bookings"] if booking["id"] == event_booking.id
        )
        assert event_booking_json["stock"]["offer"]["bookingContact"] == "contact@example.net"

        digital_booking_json = next(
            booking for booking in response.json["ongoing_bookings"] if booking["id"] == digital_booking.id
        )
        assert digital_booking_json["activationCode"]

        assert [b["id"] for b in response.json["ended_bookings"]] == [
            ended_digital_booking.id,
            cancelled_permanent_booking.id,
            cancelled.id,
            used2.id,
            used1.id,
        ]

        assert response.json["hasBookingsAfter18"] is True

        used2_json = next(booking for booking in response.json["ended_bookings"] if booking["id"] == used2.id)
        assert used2_json == {
            "enablePopUpReaction": False,
            "canReact": False,
            "userReaction": None,
            "activationCode": None,
            "cancellationDate": None,
            "cancellationReason": None,
            "confirmationDate": "2023-03-02T00:00:00Z",
            "completedUrl": f"https://demo.pass/some/path?token={used2.token}&email=pascal.ture@example.com&offerId={humanize(used2.stock.offer.id)}",
            "dateCreated": used2.dateCreated.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "dateUsed": "2023-03-02T00:00:00Z",
            "expirationDate": None,
            "quantity": 1,
            "qrCodeData": None,
            "id": used2.id,
            "stock": {
                "beginningDatetime": None,
                "features": ["VO"],
                "id": used2.stock.id,
                "price": used2.stock.price * 100,
                "priceCategoryLabel": None,
                "offer": {
                    "address": {
                        "city": used2.stock.offer.offererAddress.address.city,
                        "coordinates": {
                            "latitude": float(used2.stock.offer.offererAddress.address.latitude),
                            "longitude": float(used2.stock.offer.offererAddress.address.longitude),
                        },
                        "label": used2.stock.offer.offererAddress.label,
                        "postalCode": used2.stock.offer.offererAddress.address.postalCode,
                        "street": used2.stock.offer.offererAddress.address.street,
                        "timezone": used2.stock.offer.offererAddress.address.timezone,
                    },
                    "bookingContact": None,
                    "subcategoryId": subcategories.ABO_LIVRE_NUMERIQUE.id,
                    "extraData": None,
                    "id": used2.stock.offer.id,
                    "image": {"credit": "street credit", "url": mediation.thumbUrl},
                    "isDigital": True,
                    "isPermanent": False,
                    "name": used2.stock.offer.name,
                    "url": "https://demo.pass/some/path?token={token}&email={email}&offerId={offerId}",
                    "venue": {
                        "id": used2.venue.id,
                        "name": used2.venue.name,
                        "publicName": used2.venue.publicName,
                        # FIXME bdalbianco 28/04/2025 CLEAN_OA: check timezone relevance after regul venue
                        "timezone": "Europe/Paris",
                        "bannerUrl": None,
                        "isOpenToPublic": False,
                    },
                    "withdrawalDetails": None,
                    "withdrawalType": None,
                    "withdrawalDelay": None,
                },
            },
            "token": used2.token,
            "totalAmount": Decimal(1010),
            "externalBookings": [],
        }

        for booking in response.json["ongoing_bookings"]:
            assert booking["qrCodeData"] is not None

    def test_get_bookings_returns_user_reaction(self, client):
        now = date_utils.get_naive_utc_now()
        stock = offers_factories.EventStockFactory()
        ongoing_booking = booking_factories.BookingFactory(
            stock=stock, user__deposit__expirationDate=now + timedelta(days=180)
        )

        client = client.with_token(ongoing_booking.user)
        with assert_num_queries(2):
            # select user, booking
            response = client.get("/native/v1/bookings")

        assert response.status_code == 200
        assert response.json["ongoing_bookings"][0]["userReaction"] is None

    def test_get_bookings_returns_user_reaction_when_one_exists(self, client):
        now = date_utils.get_naive_utc_now()
        stock = offers_factories.EventStockFactory()
        ongoing_booking = booking_factories.BookingFactory(
            stock=stock, user__deposit__expirationDate=now + timedelta(days=180)
        )
        ReactionFactory(user=ongoing_booking.user, offer=stock.offer)

        client = client.with_token(ongoing_booking.user)
        with assert_num_queries(2):
            # select user, booking
            response = client.get("/native/v1/bookings")

        assert response.status_code == 200
        assert response.json["ongoing_bookings"][0]["userReaction"] == "NO_REACTION"

    def test_get_bookings_returns_user_reaction_when_reaction_is_on_the_product(self, client):
        now = date_utils.get_naive_utc_now()
        product = offers_factories.ProductFactory()
        stock = offers_factories.EventStockFactory(offer__product=product)
        ongoing_booking = booking_factories.BookingFactory(
            stock=stock, user__deposit__expirationDate=now + timedelta(days=180)
        )
        ReactionFactory(reactionType=ReactionTypeEnum.LIKE, user=ongoing_booking.user, product=stock.offer.product)
        client = client.with_token(ongoing_booking.user)
        with assert_num_queries(3):
            # select user, booking, offer
            response = client.get("/native/v1/bookings")

        assert response.status_code == 200
        assert response.json["ongoing_bookings"][0]["userReaction"] == "LIKE"

    def test_get_bookings_returns_enable_pop_up_reaction(self, client):
        offer = offers_factories.OfferFactory(
            subcategoryId=subcategories.SEANCE_CINE.id,
        )
        booking = booking_factories.UsedBookingFactory(
            stock__offer=offer,
            dateUsed=date_utils.get_naive_utc_now() - timedelta(seconds=60 * 24 * 3600),
        )
        client = client.with_token(booking.user)
        with assert_num_queries(2):
            # select user, booking, offer
            response = client.get("/native/v1/bookings")

        assert response.status_code == 200
        assert response.json["ongoing_bookings"][0]["enablePopUpReaction"] == True

    def test_get_bookings_returns_stock_price_and_price_category_label(self, client):
        now = date_utils.get_naive_utc_now()
        stock = offers_factories.EventStockFactory()
        ongoing_booking = booking_factories.BookingFactory(
            stock=stock, user__deposit__expirationDate=now + timedelta(days=180)
        )
        booking_factories.BookingFactory(stock=stock, user=ongoing_booking.user, status=BookingStatus.CANCELLED)
        client = client.with_token(ongoing_booking.user)
        with assert_num_queries(2):
            # select user, booking
            response = client.get("/native/v1/bookings")

        assert response.status_code == 200
        assert (
            response.json["ended_bookings"][0]["stock"]["priceCategoryLabel"]
            == stock.priceCategory.priceCategoryLabel.label
        )
        assert response.json["ended_bookings"][0]["stock"]["price"] == stock.price * 100
        assert (
            response.json["ongoing_bookings"][0]["stock"]["priceCategoryLabel"]
            == stock.priceCategory.priceCategoryLabel.label
        )
        assert response.json["ongoing_bookings"][0]["stock"]["price"] == stock.price * 100

    def test_get_free_bookings_in_subcategory(self, client):
        user = users_factories.BeneficiaryGrant18Factory(email=self.identifier)
        ongoing_booking = booking_factories.UsedBookingFactory(
            user=user, stock=offers_factories.StockFactory(price=0, offer__subcategoryId=subcategories.CARTE_MUSEE.id)
        )
        ended_booking = booking_factories.UsedBookingFactory(
            user=user, stock=offers_factories.StockFactory(price=10, offer__subcategoryId=subcategories.CARTE_MUSEE.id)
        )

        client = client.with_token(ongoing_booking.user)
        with assert_num_queries(2):
            # select user, booking
            response = client.get("/native/v1/bookings")

        assert response.status_code == 200
        assert response.json["ongoing_bookings"][0]["id"] == ongoing_booking.id
        assert response.json["ended_bookings"][0]["id"] == ended_booking.id

    def test_get_bookings_15_17_user(self, client):
        user = users_factories.UnderageBeneficiaryFactory(email=self.identifier)

        booking = booking_factories.UsedBookingFactory(
            user=user,
            stock__offer__subcategoryId=subcategories.TELECHARGEMENT_LIVRE_AUDIO.id,
        )

        test_client = client.with_token(user)
        with assert_num_queries(2):
            # select user, booking
            response = test_client.get("/native/v1/bookings")

        assert response.status_code == 200
        assert response.json["ongoing_bookings"][0]["id"] == booking.id
        assert response.json["hasBookingsAfter18"] is False

    def test_get_bookings_withdrawal_informations(self, client):
        user = users_factories.BeneficiaryGrant18Factory(email=self.identifier)
        booking_factories.BookingFactory(
            user=user,
            stock__offer__subcategoryId=subcategories.CONCERT.id,
            stock__offer__withdrawalDetails="Veuillez chercher votre billet au guichet",
            stock__offer__withdrawalType=offer_models.WithdrawalTypeEnum.ON_SITE,
            stock__offer__withdrawalDelay=60 * 30,
        )

        client.with_token(user)
        with assert_num_queries(2):  # user + booking
            response = client.get("/native/v1/bookings")
            assert response.status_code == 200

        offer = response.json["ongoing_bookings"][0]["stock"]["offer"]
        assert offer["withdrawalDetails"] == "Veuillez chercher votre billet au guichet"
        assert offer["withdrawalType"] == "on_site"
        assert offer["withdrawalDelay"] == 60 * 30

    @pytest.mark.features(ENABLE_CDS_IMPLEMENTATION=True)
    def test_get_bookings_with_external_booking_infos(self, client):
        user = users_factories.BeneficiaryGrant18Factory(email=self.identifier)

        provider = providers_api.get_provider_by_local_class("CDSStocks")
        booking = booking_factories.BookingFactory(
            user=user,
            stock__offer__subcategoryId=subcategories.SEANCE_CINE.id,
            stock__idAtProviders="11#11#CDS",
            stock__lastProvider=provider,
            stock__offer__lastProvider=provider,
        )
        ExternalBookingFactory(booking=booking, barcode="111111111", seat="A_1")
        ExternalBookingFactory(booking=booking, barcode="111111112", seat="A_2")

        client.with_token(user)
        with assert_num_queries(2):  # user + booking
            response = client.get("/native/v1/bookings")
            assert response.status_code == 200

        booking_response = response.json["ongoing_bookings"][0]
        assert booking_response["token"] is None  # do not display CM when it is an external booking
        assert booking_response["qrCodeData"] is not None
        assert sorted(booking_response["externalBookings"], key=lambda x: x["barcode"]) == [
            {"barcode": "111111111", "seat": "A_1"},
            {"barcode": "111111112", "seat": "A_2"},
        ]

    def test_get_bookings_with_address_on_venue(self, client):
        user = users_factories.BeneficiaryGrant18Factory(email=self.identifier)

        address = AddressFactory()
        venue = offerers_factories.VenueFactory(offererAddress__address=address)
        offer = offers_factories.OfferFactory(venue=venue, offererAddress=None)
        booking_factories.BookingFactory(stock__offer=offer, user=user)

        client.with_token(user)
        with assert_num_queries(2):  # user + booking
            response = client.get("/native/v1/bookings")

        assert response.status_code == 200
        assert response.json["ongoing_bookings"][0]["stock"]["offer"]["address"]["label"] == venue.offererAddress.label
        assert response.json["ongoing_bookings"][0]["stock"]["offer"]["address"]["city"] == address.city

    def test_get_bookings_user_19_yo(self, client):
        user = users_factories.BeneficiaryFactory(age=19)
        booking_factories.BookingFactory(user=user)

        client = client.with_token(user)
        with assert_num_queries(2):  # user + booking
            response = client.get("/native/v1/bookings")

        assert response.status_code == 200
        assert response.json["hasBookingsAfter18"] is True

    def test_return_venue_public_name(self, client):
        venue = offerers_factories.VenueFactory(name="Legal name", publicName="Public name")
        booking = booking_factories.BookingFactory(stock__offer__venue=venue)

        client = client.with_token(booking.user)
        response = client.get("/native/v1/bookings")

        assert response.status_code == 200
        assert response.json["ongoing_bookings"][0]["stock"]["offer"]["venue"]["name"] == "Public name"

    def test_return_venue_banner_url(self, client):
        venue = offerers_factories.VenueFactory(bannerUrl="http://bannerUrl.com")
        booking = booking_factories.BookingFactory(stock__offer__venue=venue)

        client = client.with_token(booking.user)
        response = client.get("/native/v1/bookings")

        assert response.status_code == 200
        assert response.json["ongoing_bookings"][0]["stock"]["offer"]["venue"]["bannerUrl"] == "http://bannerUrl.com"

    def test_return_venue_is_open_to_public(self, client):
        venue = offerers_factories.VenueFactory(isOpenToPublic=True)
        booking = booking_factories.BookingFactory(stock__offer__venue=venue)

        client = client.with_token(booking.user)
        response = client.get("/native/v1/bookings")

        assert response.status_code == 200
        assert response.json["ongoing_bookings"][0]["stock"]["offer"]["venue"]["isOpenToPublic"] is True


class CancelBookingTest:
    identifier = "pascal.ture@example.com"

    def test_cancel_booking(self, client):
        user = users_factories.BeneficiaryGrant18Factory(email=self.identifier)
        booking = booking_factories.BookingFactory(user=user)

        client = client.with_token(user)
        with assert_num_queries(28):
            response = client.post(f"/native/v1/bookings/{booking.id}/cancel")

        assert response.status_code == 204

        booking = db.session.get(Booking, booking.id)
        assert booking.status == BookingStatus.CANCELLED
        assert booking.cancellationReason == BookingCancellationReasons.BENEFICIARY
        assert len(mails_testing.outbox) == 1

    def test_cancel_booking_trigger_recredit_event(self, client):
        user = users_factories.BeneficiaryGrant18Factory(email=self.identifier)
        initial_deposit_amount = user.deposit.amount
        booking = booking_factories.BookingFactory(user=user)

        client = client.with_token(user)
        with assert_num_queries(28):
            response = client.post(f"/native/v1/bookings/{booking.id}/cancel")

        assert response.status_code == 204

        booking = db.session.get(Booking, booking.id)
        assert len(push_testing.requests) == 3
        assert push_testing.requests[0] == {
            "can_be_asynchronously_retried": True,
            "event_name": "recredit_account_cancellation",
            "event_payload": {
                "credit": Decimal(initial_deposit_amount),
                "formatted_credit": "150 €",
                "offer_id": booking.stock.offer.id,
                "offer_name": booking.stock.offer.name,
                "offer_price": Decimal("10.1"),
                "formatted_offer_price": "10,10 €",
            },
            "user_id": user.id,
        }

    def test_cancel_booking_trigger_recredit_event_for_caledonian_user(self, client):
        user = users_factories.BeneficiaryGrant18Factory(email=self.identifier, postalCode="98818")
        booking = booking_factories.BookingFactory(user=user)

        client = client.with_token(user)
        with assert_num_queries(28):
            response = client.post(f"/native/v1/bookings/{booking.id}/cancel")

        assert response.status_code == 204

        booking = db.session.get(Booking, booking.id)
        assert len(push_testing.requests) == 3
        assert push_testing.requests[0] == {
            "can_be_asynchronously_retried": True,
            "event_name": "recredit_account_cancellation",
            "event_payload": {
                "credit": Decimal("150"),
                "formatted_credit": "17900 F",
                "offer_id": booking.stock.offer.id,
                "offer_name": booking.stock.offer.name,
                "offer_price": Decimal("10.1"),
                "formatted_offer_price": "1205 F",
            },
            "user_id": user.id,
        }

    def test_cancel_others_booking(self, client):
        user = users_factories.BeneficiaryGrant18Factory(email=self.identifier)
        booking = booking_factories.BookingFactory()

        client = client.with_token(user)
        # fetch booking
        # fetch user
        # fetch booking (by email cloud task)
        with assert_num_queries(3):
            response = client.post(f"/native/v1/bookings/{booking.id}/cancel")

        assert response.status_code == 404

    def test_cancel_confirmed_booking(self, client):
        user = users_factories.BeneficiaryGrant18Factory(email=self.identifier)
        booking = booking_factories.BookingFactory(
            user=user, cancellation_limit_date=date_utils.get_naive_utc_now() - timedelta(days=1)
        )

        client = client.with_token(user)
        # fetch booking
        # fetch user
        # fetch booking (by email cloud task)
        with assert_num_queries(3):
            response = client.post(f"/native/v1/bookings/{booking.id}/cancel")

        assert response.status_code == 400
        assert response.json == {
            "code": "CONFIRMED_BOOKING",
            "message": "La date limite d'annulation est dépassée.",
        }

    def test_cancel_cancelled_booking(self, client):
        user = users_factories.BeneficiaryGrant18Factory(email=self.identifier)
        booking = booking_factories.BookingFactory(
            user=user,
            status=BookingStatus.CANCELLED,
            cancellationReason=BookingCancellationReasons.BENEFICIARY,
        )

        client = client.with_token(user)
        # fetch booking
        # fetch user
        # fetch booking (by email cloud task)
        with assert_num_queries(3):
            response = client.post(f"/native/v1/bookings/{booking.id}/cancel")

        # successful but it does nothing, so it does not send a new cancellation email
        assert response.status_code == 204
        assert len(mails_testing.outbox) == 0

    @patch("pcapi.core.bookings.api._cancel_external_booking")
    def test_unexpected_offer_provider(self, mocked_cancel_external_booking, client):
        user = users_factories.BeneficiaryGrant18Factory(email=self.identifier)
        cds_provider = providers_api.get_provider_by_local_class("CDSStocks")
        venue_provider = providers_factories.VenueProviderFactory(provider=cds_provider)
        providers_factories.CinemaProviderPivotFactory(
            venue=venue_provider.venue,
            provider=venue_provider.provider,
            idAtProvider=venue_provider.venueIdAtOfferProvider,
        )
        offer = offers_factories.EventOfferFactory(
            name="Séance ciné solo",
            venue=venue_provider.venue,
            subcategoryId=subcategories.SEANCE_CINE.id,
            lastProviderId=cds_provider.id,
        )
        stock = offers_factories.EventStockFactory(offer=offer, idAtProviders="1111%4444#111/datetime")
        booking = booking_factories.BookingFactory(user=user, stock=stock)
        booking_factories.ExternalBookingFactory(booking=booking)
        mocked_cancel_external_booking.side_effect = UnexpectedCinemaProvider("Unknown Provider: Toto")

        client = client.with_token(user)
        response = client.post(f"/native/v1/bookings/{booking.id}/cancel")

        assert response.status_code == 400
        assert response.json["external_booking"] == "L'annulation de réservation a échoué."

    @patch("pcapi.core.bookings.api._cancel_external_booking")
    def test_inactive_provider(self, mocked_cancel_external_booking, client):
        user = users_factories.BeneficiaryGrant18Factory(email=self.identifier)
        cds_provider = providers_api.get_provider_by_local_class("CDSStocks")
        venue_provider = providers_factories.VenueProviderFactory(provider=cds_provider)
        providers_factories.CinemaProviderPivotFactory(
            venue=venue_provider.venue,
            provider=venue_provider.provider,
            idAtProvider=venue_provider.venueIdAtOfferProvider,
        )
        offer = offers_factories.EventOfferFactory(
            name="Séance ciné solo",
            venue=venue_provider.venue,
            subcategoryId=subcategories.SEANCE_CINE.id,
            lastProviderId=cds_provider.id,
        )
        stock = offers_factories.EventStockFactory(offer=offer, idAtProviders="1111%4444#111/datetime")
        booking = booking_factories.BookingFactory(user=user, stock=stock)
        booking_factories.ExternalBookingFactory(booking=booking)

        mocked_cancel_external_booking.side_effect = InactiveProvider(
            f"No active cinema venue provider found for venue #{venue_provider.venue.id}"
        )

        client = client.with_token(user)
        response = client.post(f"/native/v1/bookings/{booking.id}/cancel")

        assert response.status_code == 400
        assert response.json["external_booking"] == "L'annulation de réservation a échoué."


class ToggleBookingVisibilityTest:
    identifier = "pascal.ture@example.com"

    def test_toggle_visibility(self, client):
        user = users_factories.BeneficiaryGrant18Factory(email=self.identifier)

        booking = booking_factories.BookingFactory(user=user, displayAsEnded=None)
        booking_id = booking.id

        client = client.with_token(user)
        response = client.post(f"/native/v1/bookings/{booking_id}/toggle_display", json={"ended": True})

        assert response.status_code == 204
        db.session.refresh(booking)
        assert booking.displayAsEnded

        response = client.post(f"/native/v1/bookings/{booking_id}/toggle_display", json={"ended": False})

        assert response.status_code == 204
        db.session.refresh(booking)
        assert not booking.displayAsEnded

    def test_integration_toggle_visibility(self, client):
        user = users_factories.BeneficiaryGrant18Factory(email=self.identifier)

        stock = offers_factories.StockWithActivationCodesFactory()
        activation_code = stock.activationCodes[0]
        booking = booking_factories.UsedBookingFactory(
            user=user,
            displayAsEnded=None,
            dateUsed=date_utils.get_naive_utc_now(),
            stock=stock,
            activationCode=activation_code,
        )

        client = client.with_token(user)
        with assert_num_queries(2):  # user + booking
            response = client.get("/native/v1/bookings")
            assert response.status_code == 200

        assert [b["id"] for b in response.json["ongoing_bookings"]] == [booking.id]
        assert [b["id"] for b in response.json["ended_bookings"]] == []

        response = client.post(f"/native/v1/bookings/{booking.id}/toggle_display", json={"ended": True})

        assert response.status_code == 204

        response = client.get("/native/v1/bookings")
        assert response.status_code == 200

        assert [b["id"] for b in response.json["ongoing_bookings"]] == []
        assert [b["id"] for b in response.json["ended_bookings"]] == [booking.id]

        response = client.post(f"/native/v1/bookings/{booking.id}/toggle_display", json={"ended": False})

        assert response.status_code == 204

        response = client.get("/native/v1/bookings")
        assert response.status_code == 200

        assert [b["id"] for b in response.json["ongoing_bookings"]] == [booking.id]
        assert [b["id"] for b in response.json["ended_bookings"]] == []
