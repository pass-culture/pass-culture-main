import dataclasses
from datetime import datetime
from datetime import timezone

from freezegun import freeze_time
import pytest

from pcapi.core.bookings.factories import IndividualBookingFactory
from pcapi.core.bookings.factories import UsedIndividualBookingFactory
from pcapi.core.categories import subcategories
from pcapi.core.mails.models.sendinblue_models import SendinblueTransactionalEmailData
import pcapi.core.mails.testing as mails_testing
from pcapi.core.mails.transactional.bookings.booking_confirmation_to_beneficiary import (
    get_booking_confirmation_to_beneficiary_email_data,
)
from pcapi.core.mails.transactional.bookings.booking_confirmation_to_beneficiary import (
    send_individual_booking_confirmation_email_to_beneficiary,
)
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
import pcapi.core.offers.factories as offers_factories
from pcapi.core.offers.models import WithdrawalTypeEnum
from pcapi.utils.human_ids import humanize


pytestmark = pytest.mark.usefixtures("db_session")


@freeze_time("2021-10-15 12:48:00")
def sendinblue_send_email_test():
    individual_booking = IndividualBookingFactory(
        stock=offers_factories.EventStockFactory(price=1.99), dateCreated=datetime.utcnow()
    )
    send_individual_booking_confirmation_email_to_beneficiary(individual_booking)

    assert len(mails_testing.outbox) == 1
    assert mails_testing.outbox[0].sent_data["template"] == dataclasses.asdict(
        TransactionalEmail.BOOKING_CONFIRMATION_BY_BENEFICIARY.value
    )
    assert mails_testing.outbox[0].sent_data["params"]["OFFER_PRICE"] == "1.99 €"


def get_expected_base_sendinblue_email_data(booking, mediation, **overrides):
    email_data = SendinblueTransactionalEmailData(
        template=TransactionalEmail.BOOKING_CONFIRMATION_BY_BENEFICIARY.value,
        params={
            "USER_FIRST_NAME": booking.firstName,
            "BOOKING_DATE": "15 octobre 2021",
            "BOOKING_HOUR": "14h48",
            "OFFER_NAME": booking.stock.offer.name,
            "OFFERER_NAME": booking.offerer.name,
            "EVENT_DATE": "20 octobre 2021",
            "EVENT_HOUR": "14h48",
            "OFFER_PRICE": f"{booking.total_amount} €" if booking.stock.price > 0 else "Gratuit",
            "OFFER_TOKEN": booking.token,
            "OFFER_CATEGORY": booking.stock.offer.category,
            "VENUE_NAME": booking.stock.offer.venue.name,
            "VENUE_ADDRESS": booking.stock.offer.venue.address,
            "VENUE_POSTAL_CODE": booking.stock.offer.venue.postalCode,
            "VENUE_CITY": booking.stock.offer.venue.city,
            "ALL_BUT_NOT_VIRTUAL_THING": True,
            "ALL_THINGS_NOT_VIRTUAL_THING": False,
            "IS_EVENT": True,
            "IS_EXTERNAL": False,
            "IS_SINGLE_EVENT": True,
            "IS_DUO_EVENT": False,
            "CAN_EXPIRE": False,
            "OFFER_ID": humanize(booking.stock.offer.id),
            "MEDIATION_ID": humanize(mediation.id),
            "CODE_EXPIRATION_DATE": None,
            "IS_DIGITAL_BOOKING_WITH_ACTIVATION_CODE_AND_NO_EXPIRATION_DATE": False,
            "HAS_OFFER_URL": False,
            "DIGITAL_OFFER_URL": None,
            "OFFER_WITHDRAWAL_DETAILS": None,
            "EXPIRATION_DELAY": None,
            "BOOKING_LINK": f"https://webapp-v2.example.com/reservation/{booking.id}/details",
            "OFFER_WITHDRAWAL_TYPE": None,
            "OFFER_WITHDRAWAL_DELAY": None,
        },
    )
    email_data.params.update(overrides)
    return email_data


@freeze_time("2021-10-15 12:48:00")
def test_should_return_event_specific_data_for_email_when_offer_is_an_event_sendinblue():
    booking = IndividualBookingFactory(
        stock=offers_factories.EventStockFactory(price=23.99), dateCreated=datetime.utcnow()
    )
    mediation = offers_factories.MediationFactory(offer=booking.stock.offer)
    email_data = get_booking_confirmation_to_beneficiary_email_data(booking.individualBooking)

    expected = get_expected_base_sendinblue_email_data(booking, mediation)
    assert email_data == expected


@freeze_time("2021-10-15 12:48:00")
def test_should_return_event_specific_data_for_email_when_offer_is_a_duo_event_sendinblue():
    booking = booking = IndividualBookingFactory(
        stock=offers_factories.EventStockFactory(price=23.99), dateCreated=datetime.utcnow(), quantity=2
    )
    mediation = offers_factories.MediationFactory(offer=booking.stock.offer)

    email_data = get_booking_confirmation_to_beneficiary_email_data(booking.individualBooking)

    expected = get_expected_base_sendinblue_email_data(
        booking,
        mediation,
        IS_DUO_EVENT=True,
        IS_SINGLE_EVENT=False,
        OFFER_PRICE="47.98 €",
    )
    assert email_data == expected


@freeze_time("2021-10-15 12:48:00")
def test_should_return_thing_specific_data_for_email_when_offer_is_a_thing_sendinblue():
    stock = offers_factories.ThingStockFactory(
        price=23.99,
        offer__product__subcategoryId=subcategories.SUPPORT_PHYSIQUE_FILM.id,
        offer__name="Super bien culturel",
    )
    booking = IndividualBookingFactory(stock=stock, dateCreated=datetime.utcnow())
    mediation = offers_factories.MediationFactory(offer=booking.stock.offer)

    email_data = get_booking_confirmation_to_beneficiary_email_data(booking.individualBooking)

    expected = get_expected_base_sendinblue_email_data(
        booking,
        mediation,
        ALL_THINGS_NOT_VIRTUAL_THING=True,
        EVENT_DATE=None,
        EVENT_HOUR=None,
        IS_EVENT=False,
        IS_SINGLE_EVENT=False,
        OFFER_NAME="Super bien culturel",
        CAN_EXPIRE=True,
        EXPIRATION_DELAY=30,
        BOOKING_LINK=f"https://webapp-v2.example.com/reservation/{booking.id}/details",
    )
    assert email_data == expected


@freeze_time("2021-10-15 12:48:00")
def test_should_use_public_name_when_available_sendinblue():
    booking = IndividualBookingFactory(
        stock__offer__venue__name="LIBRAIRIE GENERALE UNIVERSITAIRE COLBERT",
        stock__offer__venue__publicName="Librairie Colbert",
        dateCreated=datetime.utcnow(),
    )
    mediation = offers_factories.MediationFactory(offer=booking.stock.offer)

    email_data = get_booking_confirmation_to_beneficiary_email_data(booking.individualBooking)

    expected = get_expected_base_sendinblue_email_data(
        booking,
        mediation,
        VENUE_NAME="Librairie Colbert",
        **{key: value for key, value in email_data.params.items() if key != "VENUE_NAME"},
    )
    assert email_data == expected


@freeze_time("2021-10-15 12:48:00")
def test_should_return_withdrawal_details_when_available_sendinblue():
    withdrawal_details = "Conditions de retrait spécifiques."
    booking = IndividualBookingFactory(
        stock__offer__withdrawalDetails=withdrawal_details,
        dateCreated=datetime.utcnow(),
    )
    mediation = offers_factories.MediationFactory(offer=booking.stock.offer)

    email_data = get_booking_confirmation_to_beneficiary_email_data(booking.individualBooking)

    expected = get_expected_base_sendinblue_email_data(
        booking,
        mediation,
        OFFER_WITHDRAWAL_DETAILS=withdrawal_details,
        **{key: value for key, value in email_data.params.items() if key != "OFFER_WITHDRAWAL_DETAILS"},
    )
    assert email_data == expected


@freeze_time("2021-10-15 12:48:00")
class DigitalOffersTestSendinblue:
    def test_should_return_digital_thing_specific_data_for_email_when_offer_is_a_digital_thing_sendinblue(self):
        booking = IndividualBookingFactory(
            quantity=10,
            stock__price=0,
            stock__offer__product__subcategoryId=subcategories.VOD.id,
            stock__offer__product__url="http://example.com",
            stock__offer__name="Super offre numérique",
            dateCreated=datetime.utcnow(),
        )
        mediation = offers_factories.MediationFactory(offer=booking.stock.offer)

        email_data = get_booking_confirmation_to_beneficiary_email_data(booking.individualBooking)

        expected = get_expected_base_sendinblue_email_data(
            booking,
            mediation,
            ALL_BUT_NOT_VIRTUAL_THING=False,
            ALL_THINGS_NOT_VIRTUAL_THING=False,
            EVENT_DATE=None,
            EVENT_HOUR=None,
            IS_EVENT=False,
            IS_SINGLE_EVENT=False,
            OFFER_NAME="Super offre numérique",
            OFFER_PRICE="Gratuit",
            CAN_EXPIRE=False,
            HAS_OFFER_URL=True,
            DIGITAL_OFFER_URL="http://example.com",
            EXPIRATION_DELAY=None,
        )
        assert email_data == expected

    def test_hide_cancellation_policy_on_bookings_with_activation_code_sendinblue(self):
        offer = offers_factories.OfferFactory(
            venue__name="Lieu de l'offreur",
            venue__managingOfferer__name="Théâtre du coin",
            product=offers_factories.DigitalProductFactory(name="Super offre numérique", url="http://example.com"),
        )
        digital_stock = offers_factories.StockWithActivationCodesFactory()
        first_activation_code = digital_stock.activationCodes[0]
        booking = UsedIndividualBookingFactory(
            stock__offer=offer,
            activationCode=first_activation_code,
            dateCreated=datetime(2018, 1, 1),
        )

        mediation = offers_factories.MediationFactory(offer=booking.stock.offer)

        email_data = get_booking_confirmation_to_beneficiary_email_data(booking.individualBooking)
        expected = get_expected_base_sendinblue_email_data(
            booking,
            mediation,
            ALL_BUT_NOT_VIRTUAL_THING=False,
            ALL_THINGS_NOT_VIRTUAL_THING=False,
            EVENT_DATE=None,
            EVENT_HOUR=None,
            IS_EVENT=False,
            IS_SINGLE_EVENT=False,
            OFFER_NAME="Super offre numérique",
            OFFER_PRICE="10.00 €",
            OFFER_TOKEN=booking.activationCode.code,
            CAN_EXPIRE=False,
            IS_DIGITAL_BOOKING_WITH_ACTIVATION_CODE_AND_NO_EXPIRATION_DATE=True,
            HAS_OFFER_URL=True,
            DIGITAL_OFFER_URL="http://example.com",
            USER_FIRST_NAME="Jeanne",
            VENUE_ADDRESS="1 boulevard Poissonnière",
            VENUE_CITY="Paris",
            VENUE_POSTAL_CODE="75000",
            BOOKING_DATE="1 janvier 2018",
            BOOKING_HOUR="01h00",
            EXPIRATION_DELAY=None,
        )

        assert email_data == expected

    def test_use_activation_code_instead_of_token_if_possible_sendinblue(self):
        booking = IndividualBookingFactory(
            individualBooking__user__email="used-email@example.com",
            quantity=10,
            stock__price=0,
            stock__offer__product__subcategoryId=subcategories.VOD.id,
            stock__offer__product__url="http://example.com?token={token}&offerId={offerId}&email={email}",
            stock__offer__name="Super offre numérique",
            dateCreated=datetime.utcnow(),
        )
        offers_factories.ActivationCodeFactory(stock=booking.stock, booking=booking, code="code_toto")
        mediation = offers_factories.MediationFactory(offer=booking.stock.offer)

        email_data = get_booking_confirmation_to_beneficiary_email_data(booking.individualBooking)

        expected = get_expected_base_sendinblue_email_data(
            booking,
            mediation,
            ALL_BUT_NOT_VIRTUAL_THING=False,
            ALL_THINGS_NOT_VIRTUAL_THING=False,
            EVENT_DATE=None,
            EVENT_HOUR=None,
            IS_EVENT=False,
            IS_SINGLE_EVENT=False,
            OFFER_NAME="Super offre numérique",
            OFFER_PRICE="Gratuit",
            CAN_EXPIRE=False,
            OFFER_TOKEN="code_toto",
            IS_DIGITAL_BOOKING_WITH_ACTIVATION_CODE_AND_NO_EXPIRATION_DATE=1,
            CODE_EXPIRATION_DATE=None,
            HAS_OFFER_URL=True,
            DIGITAL_OFFER_URL=f"http://example.com?token=code_toto&offerId={humanize(booking.stock.offer.id)}&email=used-email@example.com",
            EXPIRATION_DELAY=None,
        )
        assert email_data == expected

    def test_add_expiration_date_from_activation_code_sendinblue(self):
        booking = IndividualBookingFactory(
            quantity=10,
            stock__price=0,
            stock__offer__product__subcategoryId=subcategories.VOD.id,
            stock__offer__product__url="http://example.com",
            stock__offer__name="Super offre numérique",
            dateCreated=datetime.utcnow(),
        )
        offers_factories.ActivationCodeFactory(
            stock=booking.stock,
            booking=booking,
            code="code_toto",
            expirationDate=datetime(2030, 1, 1),
        )
        mediation = offers_factories.MediationFactory(offer=booking.stock.offer)

        email_data = get_booking_confirmation_to_beneficiary_email_data(booking.individualBooking)

        expected = get_expected_base_sendinblue_email_data(
            booking,
            mediation,
            ALL_BUT_NOT_VIRTUAL_THING=False,
            ALL_THINGS_NOT_VIRTUAL_THING=False,
            EVENT_DATE=None,
            EVENT_HOUR=None,
            IS_EVENT=False,
            IS_SINGLE_EVENT=False,
            OFFER_NAME="Super offre numérique",
            OFFER_PRICE="Gratuit",
            CAN_EXPIRE=False,
            OFFER_TOKEN="code_toto",
            CODE_EXPIRATION_DATE="1 janvier 2030",
            HAS_OFFER_URL=True,
            DIGITAL_OFFER_URL="http://example.com",
            EXPIRATION_DELAY=None,
        )
        assert email_data == expected


def test_should_return_total_price_for_duo_offers_sendinblue():
    booking = IndividualBookingFactory(quantity=2, stock__price=10)
    email_data = get_booking_confirmation_to_beneficiary_email_data(booking.individualBooking)
    assert email_data.params["OFFER_PRICE"] == "20.00 €"


def test_digital_offer_without_departement_code_information_sendinblue():
    """
    Test that a user without any postal code information can book a digital
    offer. The booking date information should use the default timezone:
    metropolitan France.
    """
    offer = offers_factories.DigitalOfferFactory()
    stock = offers_factories.StockFactory(offer=offer)
    date_created = datetime(2021, 7, 1, 10, 0, 0, tzinfo=timezone.utc)
    booking = IndividualBookingFactory(stock=stock, dateCreated=date_created)

    email_data = get_booking_confirmation_to_beneficiary_email_data(booking.individualBooking)
    assert email_data.params["BOOKING_DATE"] == "1 juillet 2021"
    assert email_data.params["BOOKING_HOUR"] == "12h00"


@freeze_time("2021-10-15 12:48:00")
class BooksBookingExpirationDateTestSendinblue:
    def test_should_return_new_expiration_delay_data_for_email_when_offer_is_a_book_sendinblue(self):
        booking = IndividualBookingFactory(
            stock__offer__product__subcategoryId=subcategories.LIVRE_PAPIER.id,
            stock__offer__name="Super livre",
            dateCreated=datetime.utcnow(),
        )
        mediation = offers_factories.MediationFactory(offer=booking.stock.offer)

        email_data = get_booking_confirmation_to_beneficiary_email_data(booking.individualBooking)

        expected = get_expected_base_sendinblue_email_data(
            booking,
            mediation,
            ALL_THINGS_NOT_VIRTUAL_THING=True,
            EVENT_DATE=None,
            EVENT_HOUR=None,
            IS_EVENT=False,
            IS_SINGLE_EVENT=False,
            OFFER_NAME="Super livre",
            CAN_EXPIRE=True,
            EXPIRATION_DELAY=10,
        )
        assert email_data == expected


class BookingWithWithdrawalTypeTest:
    def should_use_withdrawal_type_and_delay_when_available(self):
        withdrawal_type = WithdrawalTypeEnum.ON_SITE
        withdrawal_delay = 60 * 60 * 24 * 2
        booking = IndividualBookingFactory(
            stock__offer__withdrawalType=withdrawal_type,
            stock__offer__withdrawalDelay=withdrawal_delay,
            dateCreated=datetime.utcnow(),
        )

        mediation = offers_factories.MediationFactory(offer=booking.stock.offer)

        email_data = get_booking_confirmation_to_beneficiary_email_data(booking.individualBooking)

        expected = get_expected_base_sendinblue_email_data(
            booking,
            mediation,
            OFFER_WITHDRAWAL_TYPE=withdrawal_type,
            OFFER_WITHDRAWAL_DELAY="2 jours",
            **{
                key: value
                for key, value in email_data.params.items()
                if key not in ("OFFER_WITHDRAWAL_TYPE", "OFFER_WITHDRAWAL_DELAY")
            },
        )

        assert email_data == expected
