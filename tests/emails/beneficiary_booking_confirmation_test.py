from datetime import datetime
from datetime import timezone
from unittest.mock import patch

import pytest

from pcapi import models
import pcapi.core.bookings.factories as bookings_factories
import pcapi.core.recommendations.factories as recommendations_factories
from pcapi.emails.beneficiary_booking_confirmation import retrieve_data_for_beneficiary_booking_confirmation_email
from pcapi.utils.human_ids import humanize


def make_booking(**kwargs):
    attributes = dict(
        dateCreated=datetime(2019, 10, 3, 13, 24, 6, tzinfo=timezone.utc),
        token="ABC123",
        user__firstName="Joe",
        stock__beginningDatetime=datetime(2019, 11, 6, 14, 59, 5, tzinfo=timezone.utc),
        stock__price=23.99,
        stock__offer__name="Super événement",
        stock__offer__product__type=str(models.EventType.SPECTACLE_VIVANT),
        stock__offer__venue__name="Lieu de l'offreur",
        stock__offer__venue__address="25 avenue du lieu",
        stock__offer__venue__postalCode="75010",
        stock__offer__venue__city="Paris",
        stock__offer__venue__managingOfferer__name="Théâtre du coin",
    )
    attributes.update(kwargs)
    return bookings_factories.BookingFactory(**attributes)


def get_expected_base_email_data(booking, mediation, **overrides):
    email_data = {
        "FromEmail": "support@example.com",
        "MJ-TemplateID": 1163067,
        "MJ-TemplateLanguage": True,
        "To": "dev@example.com",
        "Vars": {
            "user_first_name": "Joe",
            "booking_date": "3 octobre",
            "booking_hour": "15h24",
            "offer_name": "Super événement",
            "offerer_name": "Théâtre du coin",
            "event_date": "6 novembre",
            "event_hour": "15h59",
            "offer_price": "23.99",
            "offer_token": "ABC123",
            "venue_name": "Lieu de l'offreur",
            "venue_address": "25 avenue du lieu",
            "venue_postal_code": "75010",
            "venue_city": "Paris",
            "all_but_not_virtual_thing": 1,
            "all_things_not_virtual_thing": 0,
            "is_event": 1,
            "is_single_event": 1,
            "is_duo_event": 0,
            "offer_id": humanize(booking.stock.offer.id),
            "mediation_id": humanize(mediation.id),
            "env": "",
        },
    }
    email_data["Vars"].update(overrides)
    return email_data


@patch("pcapi.emails.beneficiary_booking_confirmation.format_environment_for_email", return_value="")
@pytest.mark.usefixtures("db_session")
def test_should_return_event_specific_data_for_email_when_offer_is_an_event(mock_format_environment_for_email):
    booking = make_booking()
    mediation = recommendations_factories.MediationFactory(offer=booking.stock.offer)

    email_data = retrieve_data_for_beneficiary_booking_confirmation_email(booking)

    expected = get_expected_base_email_data(booking, mediation)
    assert email_data == expected


@patch("pcapi.emails.beneficiary_booking_confirmation.format_environment_for_email", return_value="")
@pytest.mark.usefixtures("db_session")
def test_should_return_event_specific_data_for_email_when_offer_is_a_duo_event(mock_format_environment_for_email):
    booking = make_booking(quantity=2)
    mediation = recommendations_factories.MediationFactory(offer=booking.stock.offer)

    email_data = retrieve_data_for_beneficiary_booking_confirmation_email(booking)

    expected = get_expected_base_email_data(
        booking,
        mediation,
        is_duo_event=1,
        is_single_event=0,
        offer_price="47.98",
    )
    assert email_data == expected


@patch("pcapi.emails.beneficiary_booking_confirmation.format_environment_for_email", return_value="")
@pytest.mark.usefixtures("db_session")
def test_should_return_thing_specific_data_for_email_when_offer_is_a_thing(mock_format_environment_for_email):
    booking = make_booking(
        stock__offer__product__type=str(models.ThingType.AUDIOVISUEL),
        stock__offer__name="Super bien culturel",
    )
    mediation = recommendations_factories.MediationFactory(offer=booking.stock.offer)

    email_data = retrieve_data_for_beneficiary_booking_confirmation_email(booking)

    expected = get_expected_base_email_data(
        booking,
        mediation,
        all_things_not_virtual_thing=1,
        event_date="",
        event_hour="",
        is_event=0,
        is_single_event=0,
        offer_name="Super bien culturel",
    )
    assert email_data == expected


@patch("pcapi.emails.beneficiary_booking_confirmation.format_environment_for_email", return_value="")
@pytest.mark.usefixtures("db_session")
def test_should_return_digital_thing_specific_data_for_email_when_offer_is_a_digital_thing(
    mock_format_environment_for_email,
):
    booking = make_booking(
        quantity=10,
        stock__price=0,
        stock__offer__product__type=str(models.ThingType.AUDIOVISUEL),
        stock__offer__product__url="http://example.com",
        stock__offer__name="Super offre numérique",
    )
    mediation = recommendations_factories.MediationFactory(offer=booking.stock.offer)

    email_data = retrieve_data_for_beneficiary_booking_confirmation_email(booking)

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
    )
    assert email_data == expected


@patch("pcapi.emails.beneficiary_booking_confirmation.feature_send_mail_to_users_enabled", return_value=True)
@pytest.mark.usefixtures("db_session")
def test_should_send_email_to_users_address_when_environment_is_production(mock_feature_send_mail_to_users_enabled):
    booking = bookings_factories.BookingFactory(user__email="joe@example.com")
    email_data = retrieve_data_for_beneficiary_booking_confirmation_email(booking)
    assert email_data["To"] == "joe@example.com"


@pytest.mark.usefixtures("db_session")
def test_should_return_total_price_for_duo_offers():
    booking = bookings_factories.BookingFactory(quantity=2, stock__price=10)
    email_data = retrieve_data_for_beneficiary_booking_confirmation_email(booking)
    assert email_data["Vars"]["offer_price"] == "20.00"
