from datetime import datetime
from datetime import timezone

import pytest

from pcapi import models
import pcapi.core.bookings.factories as bookings_factories
from pcapi.emails.offerer_booking_recap import retrieve_data_for_offerer_booking_recap_email
from pcapi.utils.human_ids import humanize


def make_booking(**kwargs):
    attributes = dict(
        dateCreated=datetime(2019, 10, 3, 13, 24, 6, tzinfo=timezone.utc),
        token="ABC123",
        user__firstName="John",
        user__lastName="Doe",
        user__email="john@example.com",
        stock__beginningDatetime=datetime(2019, 11, 6, 14, 59, 5, tzinfo=timezone.utc),
        stock__price=0,
        stock__offer__name="Super événement",
        stock__offer__product__name="Super événement",
        stock__offer__product__type=str(models.EventType.SPECTACLE_VIVANT),
        stock__offer__venue__name="Lieu de l'offreur",
        stock__offer__venue__address="25 avenue du lieu",
        stock__offer__venue__postalCode="75010",
        stock__offer__venue__city="Paris",
        stock__offer__venue__managingOfferer__name="Théâtre du coin",
    )
    attributes.update(kwargs)
    return bookings_factories.BookingFactory(**attributes)


def get_expected_base_email_data(booking, **overrides):
    offer_id = humanize(booking.stock.offer.id)
    email_data = {
        "MJ-TemplateID": 2418750,
        "MJ-TemplateLanguage": True,
        "Headers": {
            "Reply-To": "john@example.com",
        },
        "Vars": {
            "nom_offre": "Super événement",
            "nom_lieu": "Lieu de l'offreur",
            "prix": "Gratuit",
            "date": "06-Nov-2019",
            "heure": "15h59",
            "quantity": 1,
            "user_firstName": "John",
            "user_lastName": "Doe",
            "user_email": "john@example.com",
            "user_phoneNumber": "",
            "is_event": 1,
            "can_expire": 0,
            "contremarque": "ABC123",
            "ISBN": "",
            "lien_offre_pcpro": f"http://localhost:3001/offres/{offer_id}/edition",
            "offer_type": "EventType.SPECTACLE_VIVANT",
            "departement": "75",
        },
    }
    email_data["Vars"].update(overrides)
    return email_data


@pytest.mark.usefixtures("db_session")
def test_with_event():
    booking = make_booking()

    email_data = retrieve_data_for_offerer_booking_recap_email(booking)

    expected = get_expected_base_email_data(booking)
    assert email_data == expected


@pytest.mark.usefixtures("db_session")
def test_with_book():
    booking = make_booking(
        stock__offer__name="Le récit de voyage",
        stock__offer__product__extraData={"isbn": "123456789"},
        stock__offer__product__name="Le récit de voyage",
        stock__offer__product__type=str(models.ThingType.LIVRE_EDITION),
        stock__offer__venue__address=None,
        stock__offer__venue__city=None,
        stock__offer__venue__departementCode=None,
        stock__offer__venue__isVirtual=True,
        stock__offer__venue__postalCode=None,
        stock__offer__venue__siret=None,
    )

    email_data = retrieve_data_for_offerer_booking_recap_email(booking)

    expected = get_expected_base_email_data(
        booking,
        date="",
        departement="numérique",
        heure="",
        is_event=0,
        nom_offre="Le récit de voyage",
        offer_type="book",
        can_expire=1,
    )
    assert email_data == expected


@pytest.mark.usefixtures("db_session")
def test_with_book_with_missing_isbn():
    booking = make_booking(
        stock__offer__name="Le récit de voyage",
        stock__offer__product__extraData={},  # no ISBN
        stock__offer__product__name="Le récit de voyage",
        stock__offer__product__type=str(models.ThingType.LIVRE_EDITION),
        stock__offer__venue__address=None,
        stock__offer__venue__city=None,
        stock__offer__venue__departementCode=None,
        stock__offer__venue__isVirtual=True,
        stock__offer__venue__postalCode=None,
        stock__offer__venue__siret=None,
    )

    email_data = retrieve_data_for_offerer_booking_recap_email(booking)

    expected = get_expected_base_email_data(
        booking,
        date="",
        departement="numérique",
        heure="",
        is_event=0,
        nom_offre="Le récit de voyage",
        offer_type="book",
        ISBN="",
        can_expire=1,
    )
    assert email_data == expected


@pytest.mark.usefixtures("db_session")
def test_should_not_truncate_price():
    booking = make_booking(stock__price=5.86)

    email_data = retrieve_data_for_offerer_booking_recap_email(booking)

    expected = get_expected_base_email_data(booking, prix="5.86")
    assert email_data == expected


@pytest.mark.usefixtures("db_session")
def test_should_add_user_phone_number_to_vars():
    # given
    booking = make_booking(user__phoneNumber="0123456789")

    # when
    email_data = retrieve_data_for_offerer_booking_recap_email(booking)

    # then
    template_vars = email_data["Vars"]
    assert template_vars["user_phoneNumber"] == "0123456789"


@pytest.mark.usefixtures("db_session")
def test_should_add_reply_to_header_with_beneficiary_email():
    # given
    booking = make_booking(user__email="beneficiary@example.com")

    # when
    email_data = retrieve_data_for_offerer_booking_recap_email(booking)

    # then
    template_headers = email_data["Headers"]
    assert template_headers["Reply-To"] == "beneficiary@example.com"
