from datetime import timedelta

import pytest

import pcapi.core.offers.factories as offers_factories
import pcapi.core.providers.repository as providers_api
from pcapi.core.bookings import factories as booking_factories
from pcapi.core.categories import subcategories
from pcapi.core.external_bookings.factories import ExternalBookingFactory
from pcapi.core.offers import models as offer_models
from pcapi.core.testing import assert_num_queries
from pcapi.core.users import factories as users_factories
from pcapi.utils import date as date_utils


pytestmark = pytest.mark.usefixtures("db_session")


class GetBookingTest:
    identifier = "pascal.ture@example.com"

    def test_get_booking_returns_booking_when_it_exists(self, client):
        user = users_factories.BeneficiaryGrant18Factory(email=self.identifier)
        booking = booking_factories.BookingFactory(user=user, stock__features=["3D", "AVANT_PREMIERE", "PMR"])

        client.with_token(user)
        with assert_num_queries(3):  # user + bookings + booking
            response = client.get(f"/native/v3/bookings/{booking.id}")
            assert response.status_code == 200

        assert response.json == {
            "canReact": False,
            "cancellationDate": None,
            "cancellationReason": None,
            "completedUrl": booking.completedUrl,
            "confirmationDate": booking.cancellationLimitDate,
            "dateCreated": booking.dateCreated.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "dateUsed": booking.dateUsed,
            "displayAsEnded": None,
            "enablePopUpReaction": False,
            "expirationDate": booking.expirationDate.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "id": booking.id,
            "quantity": booking.quantity,
            "stock": {
                "beginningDatetime": booking.stock.beginningDatetime,
                "id": booking.stock.id,
                "isAutomaticallyUsed": False,
                "offer": {
                    "address": {
                        "city": booking.stock.offer.offererAddress.address.city,
                        "coordinates": {
                            "latitude": float(booking.stock.offer.offererAddress.address.latitude),
                            "longitude": float(booking.stock.offer.offererAddress.address.longitude),
                        },
                        "id": booking.stock.offer.offererAddress.address.id,
                        "label": booking.stock.offer.offererAddress.label,
                        "postalCode": booking.stock.offer.offererAddress.address.postalCode,
                        "street": booking.stock.offer.offererAddress.address.street,
                        "timezone": booking.stock.offer.offererAddress.address.timezone,
                    },
                    "bookingContact": booking.stock.offer.bookingContact,
                    "extraData": {"ean": None},
                    "id": booking.stock.offer.id,
                    "image": None,
                    "isDigital": booking.stock.offer.isDigital,
                    "isPermanent": booking.stock.offer.isPermanent,
                    "name": booking.stock.offer.name,
                    "subcategoryId": booking.stock.offer.subcategoryId,
                    "url": booking.stock.offer.url,
                    "venue": {
                        "address": {"id": booking.venue.offererAddress.address.id},
                        "bannerUrl": booking.venue.bannerUrl,
                        "id": booking.venue.id,
                        "isOpenToPublic": booking.venue.isOpenToPublic,
                        "name": booking.venue.publicName,
                        "publicName": booking.venue.publicName,
                        "timezone": "Europe/Paris",
                    },
                },
                "price": int(booking.stock.price * 100),
                "priceCategoryLabel": None,
                "screeningFeatures": {
                    "accessibility": {"audio": [], "mental": [], "motor": ["PMR"], "visual": []},
                    "audio": None,
                    "language": None,
                    "specialEventType": "AVANT_PREMIERE",
                    "video": "3D",
                },
            },
            "ticket": {
                "activationCode": None,
                "display": "voucher",
                "externalBooking": None,
                "token": {"data": booking.token},
                "voucher": {"data": f"PASSCULTURE:v3;TOKEN:{booking.token}"},
                "withdrawal": {"delay": None, "details": None, "type": None},
            },
            "totalAmount": int(booking.amount * 100),
            "userReaction": None,
        }

    def test_get_booking_returns_404_when_booking_does_not_exist(self, client):
        user = users_factories.BeneficiaryGrant18Factory(email=self.identifier)
        wrong_id = 1234567890
        response = client.with_token(user).get(f"/native/v3/bookings/{wrong_id}")
        assert response.status_code == 404

    def test_get_booking_returns_404_when_booking_does_not_belong_to_user(self, client):
        user = users_factories.BeneficiaryGrant18Factory(email=self.identifier)
        other_user = users_factories.BeneficiaryGrant18Factory()
        booking = booking_factories.BookingFactory(user=other_user)
        response = client.with_token(user).get(f"/native/v3/bookings/{booking.id}")
        assert response.status_code == 404


class GetBookingTicketTest:
    identifier = "pascal.ture@example.com"

    def test_get_booking_event_no_ticket(self, client):
        user = users_factories.BeneficiaryGrant18Factory(email=self.identifier)
        booking = booking_factories.BookingFactory(
            user=user,
            stock__offer__subcategoryId=subcategories.CONCERT.id,
            stock__offer__withdrawalType=offer_models.WithdrawalTypeEnum.NO_TICKET,
        )

        client.with_token(user)
        with assert_num_queries(3):  # user + bookings + booking
            response = client.get(f"/native/v3/bookings/{booking.id}")
            assert response.status_code == 200

        ticket = response.json["ticket"]
        assert ticket["display"] == "no_ticket"
        assert ticket["token"] is None
        assert ticket["voucher"] is None
        assert ticket["activationCode"] is None

    def test_get_booking_voucher_has_qr_code_data(self, client):
        user = users_factories.BeneficiaryGrant18Factory(email=self.identifier)
        booking = booking_factories.BookingFactory(
            user=user,
            stock__offer__subcategoryId=subcategories.LIVRE_PAPIER.id,
        )

        client.with_token(user)
        with assert_num_queries(3):  # user + bookings + booking
            response = client.get(f"/native/v3/bookings/{booking.id}")
            assert response.status_code == 200

        ticket = response.json["ticket"]
        assert ticket["display"] == "voucher"
        assert ticket["voucher"] is not None
        assert ticket["voucher"]["data"] is not None
        assert ticket["voucher"]["data"] == f"PASSCULTURE:v3;TOKEN:{booking.token}"

    @pytest.mark.parametrize(
        "withdrawal_delay,delta,display",
        [
            (60 * 60 * 25, 2, "email_will_be_sent"),
            (None, 1, "email_will_be_sent"),
            (60 * 60 * 49, 2, "email_sent"),
            (60 * 60 * 12, 0, "email_sent"),
        ],
    )
    def test_get_booking_ticket_by_email(self, client, withdrawal_delay, delta, display):
        user = users_factories.BeneficiaryGrant18Factory(email=self.identifier)
        beginningDatetime = date_utils.get_naive_utc_now() + timedelta(days=delta)
        booking = booking_factories.BookingFactory(
            user=user,
            stock__offer__subcategoryId=subcategories.CONCERT.id,
            stock__offer__withdrawalType=offer_models.WithdrawalTypeEnum.BY_EMAIL,
            stock__offer__withdrawalDelay=withdrawal_delay,
            stock__beginningDatetime=beginningDatetime,
        )

        client.with_token(user)
        with assert_num_queries(3):  # user + bookings + booking
            response = client.get(f"/native/v3/bookings/{booking.id}")
            assert response.status_code == 200

        ticket = response.json["ticket"]
        assert ticket["token"] is None
        assert ticket["voucher"] is None
        assert ticket["display"] == display

    def test_get_booking_digital_ticket_with_activation_code(self, client):
        user = users_factories.BeneficiaryGrant18Factory(email=self.identifier)

        digital_stock = offers_factories.StockWithActivationCodesFactory()
        booking = booking_factories.BookingFactory(
            user=user,
            stock=digital_stock,
            activationCode=digital_stock.activationCodes[0],
        )

        client.with_token(user)
        with assert_num_queries(3):  # user + bookings + booking
            response = client.get(f"/native/v3/bookings/{booking.id}")
            assert response.status_code == 200

        ticket = response.json["ticket"]
        assert ticket["token"] is None
        assert ticket["voucher"] is None
        booking_activation_code = next(code for code in digital_stock.activationCodes if code.bookingId == booking.id)
        assert ticket["activationCode"] == {
            "code": booking_activation_code.code,
            "expirationDate": None,
        }
        assert ticket["display"] == "online_code"

    def test_get_internal_event_ticket(self, client):
        user = users_factories.BeneficiaryGrant18Factory(email=self.identifier)
        booking = booking_factories.BookingFactory(
            user=user,
            stock__offer__subcategoryId=subcategories.CONCERT.id,
            stock__offer__withdrawalType=offer_models.WithdrawalTypeEnum.ON_SITE,
        )

        client.with_token(user)
        with assert_num_queries(3):  # user + bookings + booking
            response = client.get(f"/native/v3/bookings/{booking.id}")
            assert response.status_code == 200

        ticket = response.json["ticket"]

        assert ticket["voucher"] is None
        assert ticket["token"] == {
            "data": booking.token,
        }
        assert ticket["display"] == "ticket"

    def test_get_physical_event_no_ticket(self, client):
        user = users_factories.BeneficiaryGrant18Factory(email=self.identifier)
        booking = booking_factories.BookingFactory(
            user=user,
            stock__offer__subcategoryId=subcategories.CONCERT.id,
            stock__offer__withdrawalType=offer_models.WithdrawalTypeEnum.NO_TICKET,
        )

        client.with_token(user)
        with assert_num_queries(3):  # user + bookings + booking
            response = client.get(f"/native/v3/bookings/{booking.id}")
            assert response.status_code == 200

        ticket = response.json["ticket"]
        assert ticket["token"] is None
        assert ticket["voucher"] is None
        assert ticket["display"] == "no_ticket"

    @pytest.mark.features(ENABLE_CDS_IMPLEMENTATION=True)
    def test_get_external_event_ticket_visible(self, client):
        user = users_factories.BeneficiaryGrant18Factory(email=self.identifier)

        provider = providers_api.get_provider_by_local_class("CDSStocks")
        beginningDatetime = date_utils.get_naive_utc_now() + timedelta(days=1)
        booking = booking_factories.BookingFactory(
            user=user,
            stock__offer__subcategoryId=subcategories.SEANCE_CINE.id,
            stock__offer__withdrawalType=offer_models.WithdrawalTypeEnum.IN_APP,
            stock__idAtProviders="11#11#CDS",
            stock__lastProvider=provider,
            stock__offer__lastProvider=provider,
            stock__beginningDatetime=beginningDatetime,
        )
        ExternalBookingFactory(booking=booking, barcode="111111111", seat="A_1")
        ExternalBookingFactory(booking=booking, barcode="111111112", seat="A_2")

        client.with_token(user)
        with assert_num_queries(3):  # user + bookings + booking
            response = client.get(f"/native/v3/bookings/{booking.id}")
            assert response.status_code == 200

        ticket = response.json["ticket"]
        response_data = sorted(ticket["externalBooking"]["data"], key=lambda x: x["seat"])
        assert response_data == [
            {"barcode": "111111111", "seat": "A_1"},
            {"barcode": "111111112", "seat": "A_2"},
        ]

        assert ticket["token"] is None
        assert ticket["voucher"] is None
        assert ticket["display"] == "external_ticket"

    @pytest.mark.features(ENABLE_CDS_IMPLEMENTATION=True)
    def test_get_external_event_ticket_hidden(self, client):
        user = users_factories.BeneficiaryGrant18Factory(email=self.identifier)

        provider = providers_api.get_provider_by_local_class("CDSStocks")
        beginningDatetime = date_utils.get_naive_utc_now() + timedelta(days=2, seconds=200)
        booking = booking_factories.BookingFactory(
            user=user,
            stock__offer__subcategoryId=subcategories.CONFERENCE.id,
            stock__offer__withdrawalType=offer_models.WithdrawalTypeEnum.IN_APP,
            stock__idAtProviders="11#11#CDS",
            stock__lastProvider=provider,
            stock__offer__lastProvider=provider,
            stock__beginningDatetime=beginningDatetime,
        )
        ExternalBookingFactory(booking=booking, barcode="111111111", seat="A_1")
        ExternalBookingFactory(booking=booking, barcode="111111112", seat="A_2")

        client.with_token(user)
        with assert_num_queries(3):  # user + bookings + booking
            response = client.get(f"/native/v3/bookings/{booking.id}")
            assert response.status_code == 200

        ticket = response.json["ticket"]
        assert ticket["externalBooking"] == {
            "data": None,
        }

        assert ticket["token"] is None
        assert ticket["voucher"] is None
        assert ticket["display"] == "hidden_external_ticket"

    def test_get_cinema_voucher(self, client):
        user = users_factories.BeneficiaryGrant18Factory(email=self.identifier)
        booking = booking_factories.BookingFactory(
            user=user,
            stock__offer__subcategoryId=subcategories.SEANCE_CINE.id,
        )

        client.with_token(user)
        with assert_num_queries(3):  # user + bookings + booking
            response = client.get(f"/native/v3/bookings/{booking.id}")
            assert response.status_code == 200

        ticket = response.json["ticket"]
        assert ticket["token"] == {"data": booking.token}
        assert ticket["voucher"] == {"data": f"PASSCULTURE:v3;TOKEN:{booking.token}"}
        assert ticket["display"] == "cinema_voucher"
