import pytest

from pcapi.core.bookings.models import BookingStatus
from pcapi.core.users import factories as users_factories
from pcapi.domain.offers import update_is_active_status
from pcapi.model_creators.generic_creators import create_booking
from pcapi.model_creators.generic_creators import create_offerer
from pcapi.model_creators.generic_creators import create_stock
from pcapi.model_creators.generic_creators import create_venue
from pcapi.model_creators.specific_creators import create_offer_with_event_product


class UpdateIsActiveStatusTest:
    @pytest.mark.usefixtures("db_session")
    def test_activate_offer(self, app):
        # given
        offerer = create_offerer()
        venue = create_venue(offerer)
        offers = [
            create_offer_with_event_product(venue, is_active=True),
            create_offer_with_event_product(venue, is_active=False),
        ]
        status = True

        # when
        updated_offers = update_is_active_status(offers, status)

        # then
        for updated_offer in updated_offers:
            assert updated_offer.isActive

    @pytest.mark.usefixtures("db_session")
    def test_deactivate_offer(self, app):
        # given
        offerer = create_offerer()
        venue = create_venue(offerer)
        offers = [
            create_offer_with_event_product(venue, is_active=True),
            create_offer_with_event_product(venue, is_active=False),
        ]
        status = False

        # when
        updated_offers = update_is_active_status(offers, status)

        # then
        for updated_offer in updated_offers:
            assert not updated_offer.isActive

    @pytest.mark.usefixtures("db_session")
    def test_deactivate_offer_should_keep_booking_state(self, app):
        # given
        user = users_factories.UserFactory()
        offerer = create_offerer()
        venue = create_venue(offerer)
        existing_offer = create_offer_with_event_product(venue, is_active=True)
        stock = create_stock(offer=existing_offer)
        booking = create_booking(user=user, stock=stock)
        offers = [existing_offer]
        status = False

        # when
        updated_offers = update_is_active_status(offers, status)

        # then
        assert any(not updated_offer.isActive for updated_offer in updated_offers)
        assert not booking.isCancelled
        assert booking.status is not BookingStatus.CANCELLED
