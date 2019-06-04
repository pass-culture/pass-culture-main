import pytest

from models import PcObject
from models.db import db
from scripts.fill_offer_email import fill_booking_email
from tests.conftest import clean_database
from tests.test_utils import create_offer_with_thing_product, create_venue, create_offerer, create_user_offerer, create_user


class FillBookingEmailTest:
    @clean_database
    def test_should_fill_with_venue_booking_email_when_exists(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer, booking_email='venue@email.com')
        offer = create_offer_with_thing_product(venue, booking_email=None)
        PcObject.save(offer)

        # When
        fill_booking_email([offer])

        # Then
        db.session.refresh(offer)
        assert offer.bookingEmail == 'venue@email.com'

    @clean_database
    def test_should_fill_with_user_offerer_email_if_no_venue_email(self, app):
        # Given
        offerer = create_offerer()
        user = create_user(email='user_offerer@email.com')
        user_offerer = create_user_offerer(user, offerer)
        venue = create_venue(offerer, booking_email=None)
        offer = create_offer_with_thing_product(venue, booking_email=None)
        PcObject.save(offer, user_offerer)

        # When
        fill_booking_email([offer])

        # Then
        db.session.refresh(offer)
        assert offer.bookingEmail == 'user_offerer@email.com'

    @clean_database
    def test_should_do_nothing_if_existing_booking_email(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer, booking_email='venue@email.com')
        offer = create_offer_with_thing_product(venue, booking_email='offer@email.com')
        PcObject.save(offer)

        # When
        fill_booking_email([offer])

        # Then
        db.session.refresh(offer)
        assert offer.bookingEmail == 'offer@email.com'

    @clean_database
    def test_should_do_nothing_if_no_user_offerer(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer, booking_email=None)
        offer = create_offer_with_thing_product(venue, booking_email=None)
        PcObject.save(offer)

        # When
        fill_booking_email([offer])

        # Then
        db.session.refresh(offer)
        assert offer.bookingEmail == None
