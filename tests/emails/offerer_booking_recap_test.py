from datetime import datetime
from datetime import timezone
from unittest.mock import patch

import pytest

from pcapi import models
import pcapi.core.bookings.factories as bookings_factories
from pcapi.domain.stock.stock import Stock
from pcapi.emails.offerer_booking_recap import retrieve_data_for_offerer_booking_recap_email
from pcapi.model_creators.generic_creators import create_booking
from pcapi.model_creators.generic_creators import create_deposit
from pcapi.model_creators.generic_creators import create_offerer
from pcapi.model_creators.generic_creators import create_stock
from pcapi.model_creators.generic_creators import create_user
from pcapi.model_creators.generic_creators import create_venue
from pcapi.model_creators.specific_creators import create_offer_with_event_product
from pcapi.model_creators.specific_creators import create_offer_with_thing_product
from pcapi.model_creators.specific_creators import create_product_with_thing_type
from pcapi.model_creators.specific_creators import create_stock_from_offer
from pcapi.models import ThingType
from pcapi.repository import repository
from pcapi.utils.human_ids import humanize

from tests.domain_creators.generic_creators import create_domain_beneficiary


def make_booking(**kwargs):
    attributes = dict(
        dateCreated=datetime(2019, 10, 3, 13, 24, 6, tzinfo=timezone.utc),
        token='ABC123',
        user__firstName='John',
        user__lastName='Doe',
        user__email='john@example.com',
        stock__beginningDatetime=datetime(2019, 11, 6, 14, 59, 5, tzinfo=timezone.utc),
        stock__price=0,
        stock__offer__name='Super événement',
        stock__offer__product__name='Super événement',
        stock__offer__product__type=str(models.EventType.SPECTACLE_VIVANT),
        stock__offer__venue__name="Lieu de l'offreur",
        stock__offer__venue__address="25 avenue du lieu",
        stock__offer__venue__postalCode="75010",
        stock__offer__venue__city="Paris",
        stock__offer__venue__managingOfferer__name='Théâtre du coin',
    )
    attributes.update(kwargs)
    return bookings_factories.BookingFactory(**attributes)


def get_expected_base_email_data(booking, **overrides):
    offer_id = humanize(booking.stock.offer.id)
    venue_id = humanize(booking.stock.offer.venue.id)
    offerer_id = humanize(booking.stock.offer.venue.managingOfferer.id)
    email_data = {
        'FromEmail': 'support@example.com',
        'MJ-TemplateID': 1095029,
        'MJ-TemplateLanguage': True,
        'To': 'dev@example.com',
        'Vars':
            {
                'nom_offre': 'Super événement',
                'nom_lieu': "Lieu de l'offreur",
                'prix': 'Gratuit',
                'date': '06-Nov-2019',
                'heure': '15h59',
                'quantity': 1,
                'user_firstName': 'John',
                'user_lastName': 'Doe',
                'user_email': 'john@example.com',
                'is_event': 1,
                'nombre_resa': 1,
                'contremarque': 'ABC123',
                'env': '-development',
                'ISBN': '',
                'lien_offre_pcpro': f'http://localhost:3001/offres/{offer_id}?lieu={venue_id}&structure={offerer_id}',
                'offer_type': 'EventType.SPECTACLE_VIVANT',
                'departement': '75',
                'users': [
                    {
                        'firstName': 'John',
                        'lastName': 'Doe',
                        'email': 'john@example.com',
                        'contremarque': 'ABC123',
                    },
                ],
            },
    }
    email_data['Vars'].update(overrides)
    return email_data


@pytest.mark.usefixtures("db_session")
def test_with_event():
    booking = make_booking()

    email_data = retrieve_data_for_offerer_booking_recap_email(booking, [])

    expected = get_expected_base_email_data(booking)
    assert email_data == expected


@pytest.mark.usefixtures("db_session")
def test_with_book():
    booking = make_booking(
        stock__offer__product__extraData={'isbn': '123456789'},
        stock__offer__product__name='Le récit de voyage',
        stock__offer__product__type=str(models.ThingType.LIVRE_EDITION),
        stock__offer__venue__address=None,
        stock__offer__venue__city=None,
        stock__offer__venue__departementCode=None,
        stock__offer__venue__isVirtual=True,
        stock__offer__venue__postalCode=None,
        stock__offer__venue__siret=None,
    )

    email_data = retrieve_data_for_offerer_booking_recap_email(booking, [])

    expected = get_expected_base_email_data(
        booking,
        date='',
        departement='numérique',
        heure='',
        is_event=0,
        nom_offre='Le récit de voyage',
        offer_type='book',
    )
    assert email_data == expected


@pytest.mark.usefixtures("db_session")
def test_with_book_with_missing_isbn():
    booking = make_booking(
        stock__offer__product__extraData={},  # no ISBN
        stock__offer__product__name='Le récit de voyage',
        stock__offer__product__type=str(models.ThingType.LIVRE_EDITION),
        stock__offer__venue__address=None,
        stock__offer__venue__city=None,
        stock__offer__venue__departementCode=None,
        stock__offer__venue__isVirtual=True,
        stock__offer__venue__postalCode=None,
        stock__offer__venue__siret=None,
    )

    email_data = retrieve_data_for_offerer_booking_recap_email(booking, [])

    expected = get_expected_base_email_data(
        booking,
        date='',
        departement='numérique',
        heure='',
        is_event=0,
        nom_offre='Le récit de voyage',
        offer_type='book',
        ISBN='',
    )
    assert email_data == expected


@pytest.mark.usefixtures("db_session")
def test_should_not_truncate_price():
    booking = make_booking(stock__price=5.86)

    email_data = retrieve_data_for_offerer_booking_recap_email(booking, [])

    expected = get_expected_base_email_data(booking, prix='5.86')
    assert email_data == expected


@patch('pcapi.repository.feature_queries.IS_PROD', True)
@pytest.mark.usefixtures("db_session")
def test_recipients_on_production():
    booking = make_booking()
    recipients = ['1@example.com', '2@example.com']

    email_data = retrieve_data_for_offerer_booking_recap_email(booking, recipients)

    assert email_data['To'] == ', '.join(recipients)


@pytest.mark.usefixtures("db_session")
def test_recipients_when_feature_send_mail_to_users_is_disabled():
    booking = make_booking()
    recipients = ['1@example.com', '2@example.com']

    email_data = retrieve_data_for_offerer_booking_recap_email(booking, recipients)

    assert email_data['To'] == 'dev@example.com'


@pytest.mark.usefixtures("db_session")
def test_with_two_users_who_booked_the_same_offer():
    booking1 = make_booking()
    make_booking(
        token='XYZ123',
        user__firstName='Jane',
        user__lastName='Roe',
        user__email='jane@example.com',
        stock=booking1.stock,
    )

    email_data = retrieve_data_for_offerer_booking_recap_email(booking1, [])

    user_data = email_data['Vars']['users']
    assert len(user_data) == 2
    jane = {
        'firstName': 'Jane',
        'lastName': 'Roe',
        'email': 'jane@example.com',
        'contremarque': 'XYZ123',
    }
    john = {
        'firstName': 'John',
        'lastName': 'Doe',
        'email': 'john@example.com',
        'contremarque': 'ABC123',
    }
    assert sorted(user_data, key=lambda d: d['firstName']) == [jane, john]
