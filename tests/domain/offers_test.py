from datetime import datetime

from domain.offers import is_from_allocine, update_is_active_status
from models import OfferSQLEntity
from tests.conftest import clean_database
from tests.model_creators.generic_creators import (create_booking,
                                                   create_deposit,
                                                   create_offerer,
                                                   create_provider,
                                                   create_stock, create_user,
                                                   create_venue)
from tests.model_creators.specific_creators import \
    create_offer_with_event_product


class UpdateIsActiveStatusTest:
    @clean_database
    def test_activate_offer(self, app):
        # given
        offerer = create_offerer()
        venue = create_venue(offerer)
        offers = [create_offer_with_event_product(venue, is_active=True),
                  create_offer_with_event_product(venue, is_active=False)]
        status = True

        # when
        updated_offers = update_is_active_status(offers, status)

        # then
        for updated_offer in updated_offers:
            assert updated_offer.isActive

    @clean_database
    def test_deactivate_offer(self, app):
        # given
        offerer = create_offerer()
        venue = create_venue(offerer)
        offers = [create_offer_with_event_product(venue, is_active=True),
                  create_offer_with_event_product(venue, is_active=False)]
        status = False

        # when
        updated_offers = update_is_active_status(offers, status)

        # then
        for updated_offer in updated_offers:
            assert not updated_offer.isActive

    @clean_database
    def test_deactivate_offer_should_keep_booking_state(self, app):
        # given
        user = create_user()
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


class IsFromAllocineTest:
    def test_should_return_true_when_offer_is_from_allocine_provider(self):
        # Given
        offer = OfferSQLEntity()
        offer.lastProviderId = 1
        offer.lastProvider = create_provider(local_class='AllocineStocks')

        # When
        result = is_from_allocine(offer)

        # Then
        assert result is True

    def test_should_return_false_when_offer_is_from_open_agenda(self):
        # Given
        offer = OfferSQLEntity()
        offer.lastProviderId = 2
        offer.lastProvider = create_provider(local_class='OpenAgenda')

        # When
        result = is_from_allocine(offer)

        # Then
        assert result is False

    def test_should_return_false_when_offer_is_not_imported(self):
        # Given
        offer = OfferSQLEntity()
        offer.lastProvider = None

        # When
        result = is_from_allocine(offer)

        # Then
        assert result is False
