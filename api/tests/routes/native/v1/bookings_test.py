from datetime import datetime
from datetime import timedelta
from unittest.mock import patch

import pytest

from pcapi.core.bookings import factories as booking_factories
from pcapi.core.bookings.constants import FREE_OFFER_SUBCATEGORY_IDS_TO_ARCHIVE
from pcapi.core.bookings.models import Booking
from pcapi.core.bookings.models import BookingCancellationReasons
from pcapi.core.bookings.models import BookingStatus
from pcapi.core.categories import subcategories
from pcapi.core.external_bookings.factories import ExternalBookingFactory
import pcapi.core.mails.testing as mails_testing
from pcapi.core.offers.exceptions import UnexpectedCinemaProvider
import pcapi.core.offers.factories as offers_factories
from pcapi.core.offers.factories import EventStockFactory
from pcapi.core.offers.factories import MediationFactory
from pcapi.core.offers.factories import StockFactory
from pcapi.core.offers.factories import StockWithActivationCodesFactory
from pcapi.core.offers.models import WithdrawalTypeEnum
from pcapi.core.providers.exceptions import InactiveProvider
import pcapi.core.providers.factories as providers_factories
import pcapi.core.providers.repository as providers_api
from pcapi.core.testing import assert_no_duplicated_queries
from pcapi.core.testing import override_features
from pcapi.core.users import factories as users_factories
from pcapi.models import db
from pcapi.utils.human_ids import humanize


pytestmark = pytest.mark.usefixtures("db_session")


class PostBookingTest:
    identifier = "pascal.ture@example.com"

    def test_post_bookings(self, client):
        stock = StockFactory()
        user = users_factories.BeneficiaryGrant18Factory(email=self.identifier)

        client = client.with_token(self.identifier)
        response = client.post("/native/v1/bookings", json={"stockId": stock.id, "quantity": 1})

        assert response.status_code == 200

        booking = Booking.query.filter(Booking.stockId == stock.id).first()
        assert booking.userId == user.id
        assert response.json["bookingId"] == booking.id
        assert booking.status == BookingStatus.CONFIRMED

    def test_no_stock_found(self, client):
        users_factories.BeneficiaryGrant18Factory(email=self.identifier)

        client = client.with_token(self.identifier)
        response = client.post("/native/v1/bookings", json={"stockId": 400, "quantity": 1})

        assert response.status_code == 400

    def test_insufficient_credit(self, client):
        users_factories.BeneficiaryGrant18Factory(email=self.identifier)
        stock = StockFactory(price=501)

        client = client.with_token(self.identifier)
        response = client.post("/native/v1/bookings", json={"stockId": stock.id, "quantity": 1})

        assert response.status_code == 400
        assert response.json["code"] == "INSUFFICIENT_CREDIT"

    def test_already_booked(self, client):
        user = users_factories.BeneficiaryGrant18Factory(email=self.identifier)
        booking = booking_factories.BookingFactory(user=user)

        client = client.with_token(self.identifier)
        response = client.post("/native/v1/bookings", json={"stockId": booking.stock.id, "quantity": 1})

        assert response.status_code == 400
        assert response.json["code"] == "ALREADY_BOOKED"

    def test_category_forbidden(self, client):
        stock = StockFactory(offer__subcategoryId=subcategories.VISITE_VIRTUELLE.id, offer__url="affreuse-offer.com")
        users_factories.UnderageBeneficiaryFactory(email=self.identifier)

        client.with_token(self.identifier)

        response = client.post("/native/v1/bookings", json={"stockId": stock.id, "quantity": 1})

        assert response.status_code == 400
        assert response.json == {"code": "OFFER_CATEGORY_NOT_BOOKABLE_BY_USER"}

    @patch("pcapi.core.bookings.api.book_offer")
    def test_unexpected_offer_provider(self, mocked_book_offer, client):
        users_factories.BeneficiaryGrant18Factory(email=self.identifier)
        stock = offers_factories.EventStockFactory()
        mocked_book_offer.side_effect = InactiveProvider()

        client = client.with_token(self.identifier)
        response = client.post("/native/v1/bookings", json={"stockId": stock.id, "quantity": 1})

        assert response.status_code == 400
        assert response.json["external_booking"] == "Cette offre n'est plus réservable."

    @patch("pcapi.core.bookings.api.book_offer")
    def test_inactive_provider(self, mocked_book_offer, client):
        users_factories.BeneficiaryGrant18Factory(email=self.identifier)
        stock = offers_factories.EventStockFactory()
        mocked_book_offer.side_effect = InactiveProvider()

        client = client.with_token(self.identifier)
        response = client.post("/native/v1/bookings", json={"stockId": stock.id, "quantity": 1})

        assert response.status_code == 400
        assert response.json["external_booking"] == "Cette offre n'est plus réservable."

    @pytest.mark.parametrize(
        "subcategoryId,price",
        [(subcategoryId, 0) for subcategoryId in FREE_OFFER_SUBCATEGORY_IDS_TO_ARCHIVE],
    )
    def test_post_free_bookings_from_subcategories_with_archive(self, client, subcategoryId, price):
        stock = StockFactory(price=price, offer__subcategoryId=subcategoryId)
        user = users_factories.BeneficiaryGrant18Factory(email=self.identifier)

        client = client.with_token(self.identifier)
        response = client.post("/native/v1/bookings", json={"stockId": stock.id, "quantity": 1})

        assert response.status_code == 200

        booking = Booking.query.filter(Booking.stockId == stock.id).first()
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
        stock = StockFactory(price=price, offer__subcategoryId=subcategory.id)
        user = users_factories.BeneficiaryGrant18Factory(email=self.identifier)

        client = client.with_token(self.identifier)
        response = client.post("/native/v1/bookings", json={"stockId": stock.id, "quantity": 1})

        assert response.status_code == 200

        booking = Booking.query.filter(Booking.stockId == stock.id).first()
        assert booking.userId == user.id
        assert response.json["bookingId"] == booking.id
        assert booking.status == BookingStatus.CONFIRMED
        assert not booking.dateUsed


class GetBookingsTest:
    identifier = "pascal.ture@example.com"

    def test_get_bookings(self, client):
        OFFER_URL = "https://demo.pass/some/path?token={token}&email={email}&offerId={offerId}"
        user = users_factories.BeneficiaryGrant18Factory(email=self.identifier)

        permanent_booking = booking_factories.UsedBookingFactory(
            user=user,
            stock__offer__subcategoryId=subcategories.TELECHARGEMENT_LIVRE_AUDIO.id,
            dateUsed=datetime(2023, 2, 3),
        )

        event_booking = booking_factories.BookingFactory(
            user=user,
            stock=EventStockFactory(beginningDatetime=datetime.utcnow() + timedelta(days=2)),
        )

        digital_stock = StockWithActivationCodesFactory()
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
            user=user, dateCreated=datetime.utcnow() - timedelta(days=29)
        )
        used_but_in_future = booking_factories.UsedBookingFactory(
            user=user,
            dateUsed=datetime.utcnow() - timedelta(days=1),
            stock=StockFactory(beginningDatetime=datetime.utcnow() + timedelta(days=3)),
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
            cancellation_limit_date=datetime(2023, 3, 2),
        )

        mediation = MediationFactory(id=111, offer=used2.stock.offer, thumbCount=1, credit="street credit")

        client = client.with_token(self.identifier)
        with assert_no_duplicated_queries():
            response = client.get("/native/v1/bookings")

        assert response.status_code == 200
        assert [b["id"] for b in response.json["ongoing_bookings"]] == [
            expire_tomorrow.id,
            event_booking.id,
            used_but_in_future.id,
            digital_booking.id,
            permanent_booking.id,
        ]

        assert response.json["ongoing_bookings"][3]["activationCode"]

        assert [b["id"] for b in response.json["ended_bookings"]] == [
            ended_digital_booking.id,
            cancelled_permanent_booking.id,
            cancelled.id,
            used2.id,
            used1.id,
        ]

        assert response.json["hasBookingsAfter18"] is True

        assert response.json["ended_bookings"][3] == {
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
                "id": used2.stock.id,
                "price": used2.stock.price * 100,
                "priceCategoryLabel": None,
                "offer": {
                    "subcategoryId": subcategories.SUPPORT_PHYSIQUE_FILM.id,
                    "extraData": None,
                    "id": used2.stock.offer.id,
                    "image": {"credit": "street credit", "url": mediation.thumbUrl},
                    "isDigital": True,
                    "isPermanent": False,
                    "name": used2.stock.offer.name,
                    "url": "https://demo.pass/some/path?token={token}&email={email}&offerId={offerId}",
                    "venue": {
                        "address": "1 boulevard Poissonnière",
                        "postalCode": "75000",
                        "city": "Paris",
                        "coordinates": {"latitude": 48.87004, "longitude": 2.3785},
                        "id": used2.venue.id,
                        "name": used2.venue.name,
                        "publicName": used2.venue.publicName,
                    },
                    "withdrawalDetails": None,
                    "withdrawalType": None,
                    "withdrawalDelay": None,
                },
            },
            "token": used2.token,
            "totalAmount": 1010,
            "externalBookings": [],
        }

        for booking in response.json["ongoing_bookings"]:
            assert booking["qrCodeData"] is not None

    def test_get_bookings_returns_stock_price_and_price_category_label(self, client):
        now = datetime.utcnow()
        stock = EventStockFactory()
        ongoing_booking = booking_factories.BookingFactory(
            stock=stock, user__deposit__expirationDate=now + timedelta(days=180)
        )
        booking_factories.BookingFactory(stock=stock, user=ongoing_booking.user, status=BookingStatus.CANCELLED)

        with assert_no_duplicated_queries():
            response = client.with_token(ongoing_booking.user.email).get("/native/v1/bookings")

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
            user=user, stock=StockFactory(price=0, offer__subcategoryId=subcategories.ABO_MUSEE.id)
        )
        ended_booking = booking_factories.UsedBookingFactory(
            user=user, stock=StockFactory(price=10, offer__subcategoryId=subcategories.ABO_MUSEE.id)
        )

        with assert_no_duplicated_queries():
            response = client.with_token(ongoing_booking.user.email).get("/native/v1/bookings")

        assert response.status_code == 200
        assert response.json["ongoing_bookings"][0]["id"] == ongoing_booking.id
        assert response.json["ended_bookings"][0]["id"] == ended_booking.id

    def test_get_bookings_15_17_user(self, client):
        user = users_factories.UnderageBeneficiaryFactory(email=self.identifier)

        booking = booking_factories.UsedBookingFactory(
            user=user,
            stock__offer__subcategoryId=subcategories.TELECHARGEMENT_LIVRE_AUDIO.id,
        )

        test_client = client.with_token(user.email)
        with assert_no_duplicated_queries():
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
            stock__offer__withdrawalType=WithdrawalTypeEnum.ON_SITE,
            stock__offer__withdrawalDelay=60 * 30,
        )

        response = client.with_token(self.identifier).get("/native/v1/bookings")

        assert response.status_code == 200
        offer = response.json["ongoing_bookings"][0]["stock"]["offer"]
        assert offer["withdrawalDetails"] == "Veuillez chercher votre billet au guichet"
        assert offer["withdrawalType"] == "on_site"
        assert offer["withdrawalDelay"] == 60 * 30

    @override_features(ENABLE_CDS_IMPLEMENTATION=True)
    def test_get_bookings_with_external_booking_infos(self, client):
        user = users_factories.BeneficiaryGrant18Factory(email=self.identifier)
        booking = booking_factories.BookingFactory(user=user, stock__offer__subcategoryId=subcategories.SEANCE_CINE.id)
        ExternalBookingFactory(booking=booking, barcode="111111111", seat="A_1")
        ExternalBookingFactory(booking=booking, barcode="111111112", seat="A_2")

        response = client.with_token(self.identifier).get("/native/v1/bookings")

        assert response.status_code == 200
        booking_response = response.json["ongoing_bookings"][0]
        assert booking_response["token"] is None  # do not display CM when it is an external booking
        assert booking_response["qrCodeData"] is not None
        assert sorted(booking_response["externalBookings"], key=lambda x: x["barcode"]) == [
            {"barcode": "111111111", "seat": "A_1"},
            {"barcode": "111111112", "seat": "A_2"},
        ]


class CancelBookingTest:
    identifier = "pascal.ture@example.com"

    def test_cancel_booking(self, client):
        user = users_factories.BeneficiaryGrant18Factory(email=self.identifier)
        booking = booking_factories.BookingFactory(user=user)

        client = client.with_token(self.identifier)
        response = client.post(f"/native/v1/bookings/{booking.id}/cancel")

        assert response.status_code == 204

        booking = Booking.query.get(booking.id)
        assert booking.status == BookingStatus.CANCELLED
        assert booking.cancellationReason == BookingCancellationReasons.BENEFICIARY
        assert len(mails_testing.outbox) == 1

    def test_cancel_others_booking(self, client):
        users_factories.BeneficiaryGrant18Factory(email=self.identifier)
        booking = booking_factories.BookingFactory()

        client = client.with_token(self.identifier)
        response = client.post(f"/native/v1/bookings/{booking.id}/cancel")

        assert response.status_code == 404

    def test_cancel_confirmed_booking(self, client):
        user = users_factories.BeneficiaryGrant18Factory(email=self.identifier)
        booking = booking_factories.BookingFactory(
            user=user, cancellation_limit_date=datetime.utcnow() - timedelta(days=1)
        )

        client = client.with_token(self.identifier)
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

        response = client.with_token(self.identifier).post(f"/native/v1/bookings/{booking.id}/cancel")

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
        mocked_cancel_external_booking.side_effect = UnexpectedCinemaProvider("Unknown Provider: Toto")

        client = client.with_token(self.identifier)
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

        mocked_cancel_external_booking.side_effect = InactiveProvider(
            f"No active cinema venue provider found for venue #{venue_provider.venue.id}"
        )

        client = client.with_token(self.identifier)
        response = client.post(f"/native/v1/bookings/{booking.id}/cancel")

        assert response.status_code == 400
        assert response.json["external_booking"] == "L'annulation de réservation a échoué."


class ToggleBookingVisibilityTest:
    identifier = "pascal.ture@example.com"

    def test_toggle_visibility(self, client):
        user = users_factories.BeneficiaryGrant18Factory(email=self.identifier)

        booking = booking_factories.BookingFactory(user=user, displayAsEnded=None)
        booking_id = booking.id

        client = client.with_token(self.identifier)
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

        stock = StockWithActivationCodesFactory()
        activation_code = stock.activationCodes[0]
        booking = booking_factories.UsedBookingFactory(
            user=user,
            displayAsEnded=None,
            dateUsed=datetime.utcnow(),
            stock=stock,
            activationCode=activation_code,
        )

        client = client.with_token(self.identifier)
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
