from datetime import datetime
from datetime import timezone

from freezegun import freeze_time
import pytest

import pcapi.core.bookings.factories as bookings_factories
from pcapi.core.categories import subcategories
import pcapi.core.offers.factories as offers_factories
from pcapi.emails.beneficiary_booking_confirmation import retrieve_data_for_beneficiary_booking_confirmation_email
from pcapi.utils.human_ids import humanize


pytestmark = pytest.mark.usefixtures("db_session")


def make_booking(**kwargs):
    attributes = dict(
        dateCreated=datetime(2019, 10, 3, 13, 24, 6, tzinfo=timezone.utc),
        token="ABC123",
        user__firstName="Joe",
        stock__beginningDatetime=datetime(2019, 11, 6, 14, 59, 5, tzinfo=timezone.utc),
        stock__price=23.99,
        stock__offer__name="Super événement",
        stock__offer__product__subcategoryId=subcategories.SPECTACLE_REPRESENTATION.id,
        stock__offer__venue__name="Lieu de l'offreur",
        stock__offer__venue__address="25 avenue du lieu",
        stock__offer__venue__postalCode="75010",
        stock__offer__venue__city="Paris",
        stock__offer__venue__managingOfferer__name="Théâtre du coin",
    )
    attributes.update(kwargs)
    return bookings_factories.IndividualBookingFactory(**attributes)


def get_expected_base_email_data(booking, mediation, **overrides):
    email_data = {
        "MJ-TemplateID": 3094927,
        "MJ-TemplateLanguage": True,
        "Vars": {
            "user_first_name": booking.firstName,
            "booking_date": "15 octobre 2021",
            "booking_hour": "14h48",
            "offer_name": booking.stock.offer.name,
            "offerer_name": booking.offerer.name,
            "event_date": "20 octobre 2021",
            "event_hour": "14h48",
            "offer_price": f"{booking.total_amount} €" if booking.stock.price > 0 else "Gratuit",
            "offer_token": booking.token,
            "venue_name": booking.stock.offer.venue.name,
            "venue_address": booking.stock.offer.venue.address,
            "venue_postal_code": booking.stock.offer.venue.postalCode,
            "venue_city": booking.stock.offer.venue.city,
            "all_but_not_virtual_thing": 1,
            "all_things_not_virtual_thing": 0,
            "is_event": 1,
            "is_single_event": 1,
            "is_duo_event": 0,
            "can_expire": 0,
            "offer_id": humanize(booking.stock.offer.id),
            "mediation_id": humanize(mediation.id),
            "code_expiration_date": "",
            "is_digital_booking_with_activation_code_and_no_expiration_date": 0,
            "has_offer_url": 0,
            "digital_offer_url": "",
            "offer_withdrawal_details": "",
            "expiration_delay": "",
        },
    }
    email_data["Vars"].update(overrides)
    return email_data


@freeze_time("2021-10-15 12:48:00")
def test_should_return_event_specific_data_for_email_when_offer_is_an_event():
    booking = bookings_factories.IndividualBookingFactory(
        stock=offers_factories.EventStockFactory(price=23.99), dateCreated=datetime.utcnow()
    )
    mediation = offers_factories.MediationFactory(offer=booking.stock.offer)
    email_data = retrieve_data_for_beneficiary_booking_confirmation_email(booking.individualBooking)

    expected = get_expected_base_email_data(booking, mediation)
    assert email_data == expected


@freeze_time("2021-10-15 12:48:00")
def test_should_return_event_specific_data_for_email_when_offer_is_a_duo_event():
    booking = booking = bookings_factories.IndividualBookingFactory(
        stock=offers_factories.EventStockFactory(price=23.99), dateCreated=datetime.utcnow(), quantity=2
    )
    mediation = offers_factories.MediationFactory(offer=booking.stock.offer)

    email_data = retrieve_data_for_beneficiary_booking_confirmation_email(booking.individualBooking)

    expected = get_expected_base_email_data(
        booking,
        mediation,
        is_duo_event=1,
        is_single_event=0,
        offer_price="47.98 €",
    )
    assert email_data == expected


@freeze_time("2021-10-15 12:48:00")
def test_should_return_thing_specific_data_for_email_when_offer_is_a_thing():
    stock = offers_factories.ThingStockFactory(
        price=23.99,
        offer__product__subcategoryId=subcategories.SUPPORT_PHYSIQUE_FILM.id,
        offer__name="Super bien culturel",
    )
    booking = bookings_factories.IndividualBookingFactory(stock=stock, dateCreated=datetime.utcnow())
    mediation = offers_factories.MediationFactory(offer=booking.stock.offer)

    email_data = retrieve_data_for_beneficiary_booking_confirmation_email(booking.individualBooking)

    expected = get_expected_base_email_data(
        booking,
        mediation,
        all_things_not_virtual_thing=1,
        event_date="",
        event_hour="",
        is_event=0,
        is_single_event=0,
        offer_name="Super bien culturel",
        can_expire=1,
        expiration_delay=30,
    )
    assert email_data == expected


@freeze_time("2021-10-15 12:48:00")
def test_should_use_public_name_when_available():
    booking = bookings_factories.IndividualBookingFactory(
        stock__offer__venue__name="LIBRAIRIE GENERALE UNIVERSITAIRE COLBERT",
        stock__offer__venue__publicName="Librairie Colbert",
        dateCreated=datetime.utcnow(),
    )
    mediation = offers_factories.MediationFactory(offer=booking.stock.offer)

    email_data = retrieve_data_for_beneficiary_booking_confirmation_email(booking.individualBooking)

    expected = get_expected_base_email_data(
        booking,
        mediation,
        venue_name="Librairie Colbert",
        **{key: value for key, value in email_data["Vars"].items() if key != "venue_name"},
    )
    assert email_data == expected


@freeze_time("2021-10-15 12:48:00")
def test_should_return_withdrawal_details_when_available():
    withdrawal_details = "Conditions de retrait spécifiques."
    booking = bookings_factories.IndividualBookingFactory(
        stock__offer__withdrawalDetails=withdrawal_details,
        dateCreated=datetime.utcnow(),
    )
    mediation = offers_factories.MediationFactory(offer=booking.stock.offer)

    email_data = retrieve_data_for_beneficiary_booking_confirmation_email(booking.individualBooking)

    expected = get_expected_base_email_data(
        booking,
        mediation,
        offer_withdrawal_details=withdrawal_details,
        **{key: value for key, value in email_data["Vars"].items() if key != "offer_withdrawal_details"},
    )
    assert email_data == expected


@freeze_time("2021-10-15 12:48:00")
class DigitalOffersTest:
    def test_should_return_digital_thing_specific_data_for_email_when_offer_is_a_digital_thing(self):
        booking = bookings_factories.IndividualBookingFactory(
            quantity=10,
            stock__price=0,
            stock__offer__product__subcategoryId=subcategories.VOD.id,
            stock__offer__product__url="http://example.com",
            stock__offer__name="Super offre numérique",
            dateCreated=datetime.utcnow(),
        )
        mediation = offers_factories.MediationFactory(offer=booking.stock.offer)

        email_data = retrieve_data_for_beneficiary_booking_confirmation_email(booking.individualBooking)

        expected = get_expected_base_email_data(
            booking,
            mediation,
            all_but_not_virtual_thing=0,
            all_things_not_virtual_thing=0,
            event_date="",
            event_hour="",
            is_event=0,
            is_single_event=0,
            offer_name="Super offre numérique",
            offer_price="Gratuit",
            can_expire=0,
            has_offer_url=1,
            digital_offer_url="http://example.com",
            expiration_delay="",
        )
        assert email_data == expected

    def test_hide_cancellation_policy_on_bookings_with_activation_code(self):
        offer = offers_factories.OfferFactory(
            venue__name="Lieu de l'offreur",
            venue__managingOfferer__name="Théâtre du coin",
            product=offers_factories.DigitalProductFactory(name="Super offre numérique", url="http://example.com"),
        )
        digital_stock = offers_factories.StockWithActivationCodesFactory()
        first_activation_code = digital_stock.activationCodes[0]
        booking = bookings_factories.UsedIndividualBookingFactory(
            stock__offer=offer,
            activationCode=first_activation_code,
            dateCreated=datetime(2018, 1, 1),
        )

        mediation = offers_factories.MediationFactory(offer=booking.stock.offer)

        email_data = retrieve_data_for_beneficiary_booking_confirmation_email(booking.individualBooking)
        expected = get_expected_base_email_data(
            booking,
            mediation,
            all_but_not_virtual_thing=0,
            all_things_not_virtual_thing=0,
            event_date="",
            event_hour="",
            is_event=0,
            is_single_event=0,
            offer_name="Super offre numérique",
            offer_price="10.00 €",
            offer_token=booking.activationCode.code,
            can_expire=0,
            is_digital_booking_with_activation_code_and_no_expiration_date=1,
            has_offer_url=1,
            digital_offer_url="http://example.com",
            user_first_name="Jeanne",
            venue_address="1 boulevard Poissonnière",
            venue_city="Paris",
            venue_postal_code="75000",
            booking_date="1 janvier 2018",
            booking_hour="01h00",
            expiration_delay="",
        )

        assert email_data == expected

    def test_use_activation_code_instead_of_token_if_possible(self):
        booking = bookings_factories.IndividualBookingFactory(
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

        email_data = retrieve_data_for_beneficiary_booking_confirmation_email(booking.individualBooking)

        expected = get_expected_base_email_data(
            booking,
            mediation,
            all_but_not_virtual_thing=0,
            all_things_not_virtual_thing=0,
            event_date="",
            event_hour="",
            is_event=0,
            is_single_event=0,
            offer_name="Super offre numérique",
            offer_price="Gratuit",
            can_expire=0,
            offer_token="code_toto",
            is_digital_booking_with_activation_code_and_no_expiration_date=1,
            code_expiration_date="",
            has_offer_url=1,
            digital_offer_url=f"http://example.com?token=code_toto&offerId={humanize(booking.stock.offer.id)}&email=used-email@example.com",
            expiration_delay="",
        )
        assert email_data == expected

    def test_add_expiration_date_from_activation_code(self):
        booking = bookings_factories.IndividualBookingFactory(
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

        email_data = retrieve_data_for_beneficiary_booking_confirmation_email(booking.individualBooking)

        expected = get_expected_base_email_data(
            booking,
            mediation,
            all_but_not_virtual_thing=0,
            all_things_not_virtual_thing=0,
            event_date="",
            event_hour="",
            is_event=0,
            is_single_event=0,
            offer_name="Super offre numérique",
            offer_price="Gratuit",
            can_expire=0,
            offer_token="code_toto",
            code_expiration_date="1 janvier 2030",
            has_offer_url=1,
            digital_offer_url="http://example.com",
            expiration_delay="",
        )
        assert email_data == expected


def test_should_return_total_price_for_duo_offers():
    booking = bookings_factories.IndividualBookingFactory(quantity=2, stock__price=10)
    email_data = retrieve_data_for_beneficiary_booking_confirmation_email(booking.individualBooking)
    assert email_data["Vars"]["offer_price"] == "20.00 €"


def test_digital_offer_without_departement_code_information():
    """
    Test that a user without any postal code information can book a digital
    offer. The booking date information should use the default timezone:
    metropolitan France.
    """
    offer = offers_factories.DigitalOfferFactory()
    stock = offers_factories.StockFactory(offer=offer)
    date_created = datetime(2021, 7, 1, 10, 0, 0, tzinfo=timezone.utc)
    booking = bookings_factories.IndividualBookingFactory(
        stock=stock, dateCreated=date_created, user__departementCode=None
    )

    email_data = retrieve_data_for_beneficiary_booking_confirmation_email(booking.individualBooking)
    assert email_data["Vars"]["booking_date"] == "1 juillet 2021"
    assert email_data["Vars"]["booking_hour"] == "12h00"


@freeze_time("2021-10-15 12:48:00")
class BooksBookingExpirationDateTest:
    def test_should_return_new_expiration_delay_data_for_email_when_offer_is_a_book(self):
        booking = bookings_factories.IndividualBookingFactory(
            stock__offer__product__subcategoryId=subcategories.LIVRE_PAPIER.id,
            stock__offer__name="Super livre",
            dateCreated=datetime.utcnow(),
        )
        mediation = offers_factories.MediationFactory(offer=booking.stock.offer)

        email_data = retrieve_data_for_beneficiary_booking_confirmation_email(booking.individualBooking)

        expected = get_expected_base_email_data(
            booking,
            mediation,
            all_things_not_virtual_thing=1,
            event_date="",
            event_hour="",
            is_event=0,
            is_single_event=0,
            offer_name="Super livre",
            can_expire=1,
            expiration_delay=10,
        )
        assert email_data == expected
