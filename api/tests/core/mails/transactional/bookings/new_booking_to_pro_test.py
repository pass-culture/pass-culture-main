from dataclasses import asdict
from datetime import datetime
from datetime import timezone

import pytest

import pcapi.core.bookings.factories as bookings_factories
from pcapi.core.categories import subcategories
import pcapi.core.mails.testing as mails_testing
from pcapi.core.mails.transactional.bookings.new_booking_to_pro import get_new_booking_to_pro_email_data
from pcapi.core.mails.transactional.bookings.new_booking_to_pro import send_user_new_booking_to_pro_email
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
import pcapi.core.offers.factories as offers_factories
from pcapi.core.offers.factories import ActivationCodeFactory


def make_booking(**kwargs):
    attributes = dict(
        dateCreated=datetime(2019, 10, 3, 13, 24, 6, tzinfo=timezone.utc),
        token="ABC123",
        individualBooking__user__firstName="John",
        individualBooking__user__lastName="Doe",
        individualBooking__user__email="john@example.com",
        stock__beginningDatetime=datetime(2019, 11, 6, 14, 59, 5, tzinfo=timezone.utc),
        stock__price=10,
        stock__offer__name="Super événement",
        stock__offer__product__name="Super événement",
        stock__offer__product__subcategoryId=subcategories.SPECTACLE_REPRESENTATION.id,
        stock__offer__venue__name="Lieu de l'offreur",
        stock__offer__venue__address="25 avenue du lieu",
        stock__offer__venue__postalCode="75010",
        stock__offer__venue__city="Paris",
        stock__offer__venue__managingOfferer__name="Théâtre du coin",
        stock__offer__venue__departementCode="75",
    )
    attributes.update(kwargs)
    return bookings_factories.IndividualBookingFactory(**attributes)


def get_expected_base_email_data(booking, **overrides):
    email_data_params = {
        "CAN_EXPIRE": False,
        "COUNTERMARK": "ABC123",
        "DEPARTMENT_CODE": "75",
        "EVENT_DATE": "06-Nov-2019",
        "EVENT_HOUR": "15h59",
        "IS_BOOKING_AUTOVALIDATED": False,
        "IS_DIGITAL": False,
        "IS_EVENT": True,
        "IS_THING": False,
        "IS_EXTERNAL": False,
        "ISBN": "",
        "MUST_USE_TOKEN_FOR_PAYMENT": True,
        "OFFER_NAME": "Super événement",
        "OFFER_SUBCATEGORY": "SPECTACLE_REPRESENTATION",
        "PRICE": "10.00 €",
        "QUANTITY": 1,
        "USER_EMAIL": "john@example.com",
        "USER_FIRSTNAME": "John",
        "USER_LASTNAME": "Doe",
        "USER_PHONENUMBER": "",
        "VENUE_NAME": "Lieu de l'offreur",
        "WITHDRAWAL_PERIOD": 30,
    }
    email_data_params.update(overrides)
    return email_data_params


class OffererBookingRecapTest:
    @pytest.mark.usefixtures("db_session")
    def test_with_event(self):
        booking = make_booking()

        email_data = get_new_booking_to_pro_email_data(booking.individualBooking)

        expected = get_expected_base_email_data(booking)
        assert email_data.params == expected

    @pytest.mark.usefixtures("db_session")
    def test_with_book(self):
        booking = make_booking(
            stock__offer__name="Le récit de voyage",
            stock__offer__product__extraData={"isbn": "123456789"},
            stock__offer__product__name="Le récit de voyage",
            stock__offer__product__subcategoryId=subcategories.LIVRE_PAPIER.id,
        )

        email_data = get_new_booking_to_pro_email_data(booking.individualBooking)

        expected = get_expected_base_email_data(
            booking,
            EVENT_DATE="",
            EVENT_HOUR="",
            IS_EVENT=False,
            OFFER_NAME="Le récit de voyage",
            OFFER_SUBCATEGORY="book",
            CAN_EXPIRE=True,
            IS_THING=True,
            WITHDRAWAL_PERIOD=10,
        )
        assert email_data.params == expected

    @pytest.mark.usefixtures("db_session")
    def test_non_digital_bookings_can_expire_after_30_days(self):
        booking = make_booking(
            stock__offer__name="Le récit de voyage",
            stock__offer__product__extraData={"isbn": "123456789"},
            stock__offer__product__name="Le récit de voyage",
            stock__offer__product__subcategoryId=subcategories.SUPPORT_PHYSIQUE_FILM.id,
            stock__offer__venue__address=None,
            stock__offer__venue__city=None,
            stock__offer__venue__departementCode=None,
            stock__offer__venue__isVirtual=True,
            stock__offer__venue__postalCode=None,
            stock__offer__venue__siret=None,
        )

        email_data = get_new_booking_to_pro_email_data(booking.individualBooking)

        expected = get_expected_base_email_data(
            booking,
            DEPARTMENT_CODE=None,
            EVENT_DATE="",
            EVENT_HOUR="",
            IS_EVENT=False,
            IS_THING=True,
            OFFER_NAME="Le récit de voyage",
            OFFER_SUBCATEGORY="SUPPORT_PHYSIQUE_FILM",
            CAN_EXPIRE=True,
        )
        assert email_data.params == expected

    @pytest.mark.usefixtures("db_session")
    def test_with_book_with_missing_isbn(self):
        booking = make_booking(
            stock__offer__name="Le récit de voyage",
            stock__offer__product__extraData={},  # no ISBN
            stock__offer__product__name="Le récit de voyage",
            stock__offer__product__subcategoryId=subcategories.LIVRE_PAPIER.id,
            stock__offer__venue__address=None,
            stock__offer__venue__city=None,
            stock__offer__venue__departementCode=None,
            stock__offer__venue__isVirtual=True,
            stock__offer__venue__postalCode=None,
            stock__offer__venue__siret=None,
        )

        email_data = get_new_booking_to_pro_email_data(booking.individualBooking)

        expected = get_expected_base_email_data(
            booking,
            DEPARTMENT_CODE=None,
            EVENT_DATE="",
            EVENT_HOUR="",
            IS_EVENT=False,
            OFFER_NAME="Le récit de voyage",
            OFFER_SUBCATEGORY="book",
            ISBN="",
            CAN_EXPIRE=True,
            IS_THING=True,
            WITHDRAWAL_PERIOD=10,
        )
        assert email_data.params == expected

    @pytest.mark.usefixtures("db_session")
    def test_a_digital_booking_expires_after_30_days(self):
        # Given
        booking = make_booking(
            quantity=10,
            stock__price=0,
            stock__offer__product__subcategoryId=subcategories.VOD.id,
            stock__offer__product__url="http://example.com",
            stock__offer__name="Super offre numérique",
        )

        # When
        email_data = get_new_booking_to_pro_email_data(booking.individualBooking)

        # Then
        expected = get_expected_base_email_data(
            booking,
            DEPARTMENT_CODE="numérique",
            EVENT_DATE="",
            EVENT_HOUR="",
            IS_EVENT=False,
            PRICE="Gratuit",
            OFFER_NAME="Super offre numérique",
            OFFER_SUBCATEGORY="VOD",
            QUANTITY=10,
            CAN_EXPIRE=False,
            MUST_USE_TOKEN_FOR_PAYMENT=False,
            IS_THING=True,
            IS_DIGITAL=True,
        )
        assert email_data.params == expected

    @pytest.mark.usefixtures("db_session")
    def test_when_use_token_for_payment(self):
        # Given
        booking = make_booking(
            stock__price=10,
        )

        # When
        email_data = get_new_booking_to_pro_email_data(booking.individualBooking)

        # Then
        expected = get_expected_base_email_data(booking, MUST_USE_TOKEN_FOR_PAYMENT=True)
        assert email_data.params == expected

    @pytest.mark.usefixtures("db_session")
    def test_no_need_when_price_is_free(self):
        # Given
        booking = make_booking(
            stock__price=0,
        )

        # When
        email_data = get_new_booking_to_pro_email_data(booking.individualBooking)

        # Then
        expected = get_expected_base_email_data(booking, PRICE="Gratuit", MUST_USE_TOKEN_FOR_PAYMENT=False)
        assert email_data.params == expected

    @pytest.mark.usefixtures("db_session")
    def test_no_need_when_using_activation_code(self):
        # Given
        booking = make_booking()
        ActivationCodeFactory(stock=booking.stock, booking=booking, code="code_toto")

        # When
        email_data = get_new_booking_to_pro_email_data(booking.individualBooking)

        # Then
        expected = get_expected_base_email_data(booking, MUST_USE_TOKEN_FOR_PAYMENT=False)
        assert email_data.params == expected

    @pytest.mark.usefixtures("db_session")
    def test_no_need_when_booking_is_autovalidated(self):
        # Given
        offer = offers_factories.OfferFactory(
            venue__name="Lieu de l'offreur",
            venue__managingOfferer__name="Théâtre du coin",
            product=offers_factories.DigitalProductFactory(name="Super événement", url="http://example.com"),
        )
        digital_stock = offers_factories.StockWithActivationCodesFactory()
        first_activation_code = digital_stock.activationCodes[0]
        booking = bookings_factories.UsedIndividualBookingFactory(
            individualBooking__user__email="john@example.com",
            individualBooking__user__firstName="John",
            individualBooking__user__lastName="Doe",
            stock__offer=offer,
            activationCode=first_activation_code,
            dateCreated=datetime(2018, 1, 1),
        )

        # When
        email_data = get_new_booking_to_pro_email_data(booking.individualBooking)

        # Then
        expected = get_expected_base_email_data(
            booking,
            DEPARTMENT_CODE="numérique",
            EVENT_DATE="",
            EVENT_HOUR="",
            IS_EVENT=False,
            IS_BOOKING_AUTOVALIDATED=True,
            MUST_USE_TOKEN_FOR_PAYMENT=False,
            OFFER_SUBCATEGORY="VOD",
            COUNTERMARK=booking.token,
            IS_THING=True,
            IS_DIGITAL=True,
        )
        assert email_data.params == expected

    @pytest.mark.usefixtures("db_session")
    def test_a_digital_booking_with_activation_code_is_automatically_used(self):
        # Given
        offer = offers_factories.OfferFactory(
            venue__name="Lieu de l'offreur",
            venue__managingOfferer__name="Théâtre du coin",
            product=offers_factories.DigitalProductFactory(name="Super offre numérique", url="http://example.com"),
        )
        digital_stock = offers_factories.StockWithActivationCodesFactory()
        first_activation_code = digital_stock.activationCodes[0]
        booking = bookings_factories.UsedIndividualBookingFactory(
            individualBooking__user__email="john@example.com",
            individualBooking__user__firstName="John",
            individualBooking__user__lastName="Doe",
            stock__offer=offer,
            activationCode=first_activation_code,
            dateCreated=datetime(2018, 1, 1),
        )

        # When
        email_data = get_new_booking_to_pro_email_data(booking.individualBooking)

        # Then
        expected = get_expected_base_email_data(
            booking,
            DEPARTMENT_CODE="numérique",
            EVENT_DATE="",
            EVENT_HOUR="",
            PRICE="10.00 €",
            IS_EVENT=False,
            OFFER_NAME="Super offre numérique",
            OFFER_SUBCATEGORY="VOD",
            QUANTITY=1,
            CAN_EXPIRE=False,
            IS_BOOKING_AUTOVALIDATED=True,
            MUST_USE_TOKEN_FOR_PAYMENT=False,
            COUNTERMARK=booking.token,
            IS_THING=True,
            IS_DIGITAL=True,
        )
        assert email_data.params == expected

    @pytest.mark.usefixtures("db_session")
    def test_should_not_truncate_price(self):
        booking = make_booking(stock__price=5.86)

        email_data = get_new_booking_to_pro_email_data(booking.individualBooking)

        expected = get_expected_base_email_data(booking, PRICE="5.86 €")
        assert email_data.params == expected

    @pytest.mark.usefixtures("db_session")
    def test_should_use_venue_public_name_when_available(self):
        booking = make_booking(
            stock__offer__venue__name="Legal name",
            stock__offer__venue__publicName="Public name",
        )

        email_data = get_new_booking_to_pro_email_data(booking.individualBooking)

        expected = get_expected_base_email_data(booking, VENUE_NAME="Public name")
        assert email_data.params == expected

    @pytest.mark.usefixtures("db_session")
    def test_should_add_user_phone_number_to_params(self):
        # given
        booking = make_booking(individualBooking__user__phoneNumber="0123456789")

        # when
        email_data = get_new_booking_to_pro_email_data(
            booking.individualBooking,
        )

        # then
        assert email_data.params["USER_PHONENUMBER"] == "+33123456789"


class SendNewBookingEmailToProTest:
    @pytest.mark.usefixtures("db_session")
    def test_send_to_offerer(self):
        booking = bookings_factories.IndividualBookingFactory(
            individualBooking__user__email="user@example.com",
            individualBooking__user__firstName="Tom",
            individualBooking__user__lastName="P",
            stock__offer__bookingEmail="booking.email@example.com",
        )

        send_user_new_booking_to_pro_email(booking.individualBooking, first_venue_booking=False)

        assert len(mails_testing.outbox) == 1  # test number of emails sent
        assert mails_testing.outbox[0].sent_data["To"] == "booking.email@example.com"
        assert mails_testing.outbox[0].sent_data["template"] == asdict(TransactionalEmail.NEW_BOOKING_TO_PRO.value)
        assert mails_testing.outbox[0].sent_data["reply_to"] == {
            "email": "user@example.com",
            "name": "Tom P",
        }


class SendFirstVenueBookingEmailToProTest:
    @pytest.mark.usefixtures("db_session")
    def test_send_to_offerer(self):
        booking = bookings_factories.IndividualBookingFactory(
            individualBooking__user__email="user@example.com",
            individualBooking__user__firstName="Tom",
            individualBooking__user__lastName="P",
            stock__offer__venue__bookingEmail="venue@bookingEmail.app",
        )

        send_user_new_booking_to_pro_email(booking.individualBooking, first_venue_booking=True)

        assert len(mails_testing.outbox) == 1  # test number of emails sent
        assert mails_testing.outbox[0].sent_data["To"] == "venue@bookingEmail.app"
        assert mails_testing.outbox[0].sent_data["template"] == asdict(
            TransactionalEmail.FIRST_VENUE_BOOKING_TO_PRO.value
        )
        assert mails_testing.outbox[0].sent_data["reply_to"] == {
            "email": "user@example.com",
            "name": "Tom P",
        }
