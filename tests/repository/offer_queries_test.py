import pytest
from sqlalchemy import func

from pcapi.model_creators.generic_creators import create_booking
from pcapi.model_creators.generic_creators import create_offerer
from pcapi.model_creators.generic_creators import create_user
from pcapi.model_creators.generic_creators import create_venue
from pcapi.model_creators.specific_creators import create_event_occurrence
from pcapi.model_creators.specific_creators import create_offer_with_event_product
from pcapi.model_creators.specific_creators import create_offer_with_thing_product
from pcapi.model_creators.specific_creators import create_product_with_event_type
from pcapi.model_creators.specific_creators import create_product_with_thing_type
from pcapi.model_creators.specific_creators import create_stock_from_event_occurrence
from pcapi.model_creators.specific_creators import create_stock_from_offer
from pcapi.models import Offer
from pcapi.models import Stock
from pcapi.repository import repository
from pcapi.repository.offer_queries import _build_bookings_quantity_subquery
from pcapi.repository.offer_queries import get_offers_by_ids
from pcapi.repository.offer_queries import get_offers_by_venue_id
from pcapi.repository.offer_queries import get_paginated_active_offer_ids
from pcapi.repository.offer_queries import get_paginated_offer_ids_by_venue_id


class FindOffersTest:
    @pytest.mark.usefixtures("db_session")
    def test_get_offers_by_venue_id_returns_offers_matching_venue_id(self, app):
        # Given
        product = create_product_with_thing_type(thing_name="Lire un livre", is_national=True)
        offerer = create_offerer()
        venue = create_venue(offerer, postal_code="34000", departement_code="34")
        offer = create_offer_with_thing_product(venue=venue, product=product)
        repository.save(offer)

        # When
        offers = get_offers_by_venue_id(venue.id)

        # Then
        assert len(offers) == 1
        assert offers[0].venueId == venue.id


class QueryOfferWithRemainingStocksTest:
    @pytest.mark.usefixtures("db_session")
    def test_should_return_0_offer_when_there_is_no_stock(self, app):
        # Given
        thing = create_product_with_thing_type()
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue=venue, product=thing)
        repository.save(offer)

        # When
        offers_count = Offer.query.join(Stock).count()

        # Then
        assert offers_count == 0

    @pytest.mark.usefixtures("db_session")
    def test_should_return_1_offer_when_all_available_stock_is_not_booked(self, app):
        # Given
        thing = create_product_with_thing_type()
        user = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue=venue, product=thing)
        stock = create_stock_from_offer(offer, price=0, quantity=4)
        booking_1 = create_booking(user=user, stock=stock, quantity=2)
        booking_2 = create_booking(user=user, stock=stock, quantity=1)
        repository.save(stock, booking_1, booking_2)
        bookings_quantity = _build_bookings_quantity_subquery()

        # When
        offers_count = (
            Offer.query.join(Stock)
            .outerjoin(bookings_quantity, Stock.id == bookings_quantity.c.stockId)
            .filter((Stock.quantity == None) | ((Stock.quantity - func.coalesce(bookings_quantity.c.quantity, 0)) > 0))
            .count()
        )

        # Then
        assert offers_count == 1

    @pytest.mark.usefixtures("db_session")
    def test_should_return_0_offer_when_all_available_stock_is_booked(self, app):
        # Given
        thing = create_product_with_thing_type()
        user = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue=venue, product=thing)
        stock = create_stock_from_offer(offer, price=0, quantity=3)
        booking_1 = create_booking(user=user, stock=stock, quantity=2)
        booking_2 = create_booking(user=user, stock=stock, quantity=1)
        repository.save(stock, booking_1, booking_2)
        bookings_quantity = _build_bookings_quantity_subquery()

        # When
        offers_count = (
            Offer.query.join(Stock)
            .outerjoin(bookings_quantity, Stock.id == bookings_quantity.c.stockId)
            .filter((Stock.quantity == None) | ((Stock.quantity - func.coalesce(bookings_quantity.c.quantity, 0)) > 0))
            .count()
        )

        # Then
        assert offers_count == 0

    @pytest.mark.usefixtures("db_session")
    def test_should_return_1_offer_when_booking_was_cancelled(self, app):
        # Given
        user = create_user()
        product = create_product_with_thing_type(thing_name="Lire un livre", is_national=True)
        offerer = create_offerer()
        venue = create_venue(offerer, postal_code="34000", departement_code="34")
        offer = create_offer_with_thing_product(venue=venue, product=product)
        stock = create_stock_from_offer(offer, quantity=2)
        booking = create_booking(user=user, stock=stock, is_cancelled=True, quantity=2, venue=venue)
        repository.save(booking)
        bookings_quantity = _build_bookings_quantity_subquery()

        # When
        offers_count = (
            Offer.query.join(Stock)
            .outerjoin(bookings_quantity, Stock.id == bookings_quantity.c.stockId)
            .filter((Stock.quantity == None) | ((Stock.quantity - func.coalesce(bookings_quantity.c.quantity, 0)) > 0))
            .count()
        )

        # Then
        assert offers_count == 1

    @pytest.mark.usefixtures("db_session")
    def test_should_return_0_offer_when_there_is_no_remaining_stock(self):
        # Given
        product = create_product_with_thing_type(thing_name="Lire un livre", is_national=True)
        offerer = create_offerer()
        venue = create_venue(offerer, postal_code="34000", departement_code="34")
        offer = create_offer_with_thing_product(venue=venue, product=product)
        stock = create_stock_from_offer(offer, price=0, quantity=2)
        user = create_user()
        booking1 = create_booking(user=user, stock=stock, is_cancelled=True, quantity=2, venue=venue)
        booking2 = create_booking(user=user, stock=stock, quantity=2, venue=venue)
        repository.save(booking1, booking2)
        bookings_quantity = _build_bookings_quantity_subquery()

        # When
        offers_count = (
            Offer.query.join(Stock)
            .outerjoin(bookings_quantity, Stock.id == bookings_quantity.c.stockId)
            .filter((Stock.quantity == None) | ((Stock.quantity - func.coalesce(bookings_quantity.c.quantity, 0)) > 0))
            .count()
        )

        # Then
        assert offers_count == 0

    @pytest.mark.usefixtures("db_session")
    def test_should_return_1_offer_when_there_are_one_full_stock_and_one_empty_stock(self):
        # Given
        product = create_product_with_thing_type(thing_name="Lire un livre", is_national=True)
        offerer = create_offerer()
        venue = create_venue(offerer, postal_code="34000", departement_code="34")
        offer = create_offer_with_thing_product(venue=venue, product=product)
        stock1 = create_stock_from_offer(offer, price=0, quantity=2)
        stock2 = create_stock_from_offer(offer, price=0, quantity=2)
        user = create_user()
        booking1 = create_booking(user=user, stock=stock1, quantity=2, venue=venue)
        repository.save(booking1, stock2)
        bookings_quantity = _build_bookings_quantity_subquery()

        # When
        offers_count = (
            Offer.query.join(Stock)
            .outerjoin(bookings_quantity, Stock.id == bookings_quantity.c.stockId)
            .filter((Stock.quantity == None) | ((Stock.quantity - func.coalesce(bookings_quantity.c.quantity, 0)) > 0))
            .count()
        )

        # Then
        assert offers_count == 1


def _create_event_stock_and_offer_for_date(venue, date):
    product = create_product_with_event_type()
    offer = create_offer_with_event_product(venue=venue, product=product)
    event_occurrence = create_event_occurrence(offer, beginning_datetime=date)
    stock = create_stock_from_event_occurrence(event_occurrence, booking_limit_date=date)
    return stock


class GetOffersByIdsTest:
    @pytest.mark.usefixtures("db_session")
    def test_should_return_all_existing_offers_when_offer_ids_are_given(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer=offerer)
        offer1 = create_offer_with_thing_product(venue=venue)
        offer2 = create_offer_with_thing_product(venue=venue)
        repository.save(offer1, offer2)
        offer_ids = [0, offer1.id, offer2.id]

        # When
        offers = get_offers_by_ids(offer_ids)

        # Then
        assert len(offers) == 2
        assert offer1 in offers
        assert offer2 in offers


class GetPaginatedActiveOfferIdsTest:
    @pytest.mark.usefixtures("db_session")
    def test_should_return_two_offer_ids_from_first_page_when_limit_is_two_and_two_active_offers(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer=offerer)
        offer1 = create_offer_with_event_product(is_active=True, venue=venue)
        offer2 = create_offer_with_event_product(is_active=True, venue=venue)
        offer3 = create_offer_with_thing_product(is_active=True, venue=venue)
        offer4 = create_offer_with_thing_product(is_active=True, venue=venue)
        repository.save(offer1, offer2)

        # When
        offer_ids = get_paginated_active_offer_ids(limit=2, page=0)

        # Then
        assert len(offer_ids) == 2
        assert (offer1.id,) in offer_ids
        assert (offer2.id,) in offer_ids
        assert (offer3.id,) not in offer_ids
        assert (offer4.id,) not in offer_ids

    @pytest.mark.usefixtures("db_session")
    def test_should_return_one_offer_id_from_second_page_when_limit_is_1_and_three_active_offers(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer=offerer)
        offer1 = create_offer_with_event_product(is_active=True, venue=venue)
        offer2 = create_offer_with_event_product(is_active=False, venue=venue)
        offer3 = create_offer_with_thing_product(is_active=True, venue=venue)
        offer4 = create_offer_with_thing_product(is_active=True, venue=venue)
        repository.save(offer1, offer2)

        # When
        offer_ids = get_paginated_active_offer_ids(limit=1, page=1)

        # Then
        assert len(offer_ids) == 1
        assert (offer3.id,) in offer_ids
        assert (offer1.id,) not in offer_ids
        assert (offer2.id,) not in offer_ids
        assert (offer4.id,) not in offer_ids

    @pytest.mark.usefixtures("db_session")
    def test_should_return_one_offer_id_from_third_page_when_limit_is_1_and_three_active_offers(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer=offerer)
        offer1 = create_offer_with_event_product(is_active=True, venue=venue)
        offer2 = create_offer_with_event_product(is_active=False, venue=venue)
        offer3 = create_offer_with_thing_product(is_active=True, venue=venue)
        offer4 = create_offer_with_thing_product(is_active=True, venue=venue)
        repository.save(offer1, offer2)

        # When
        offer_ids = get_paginated_active_offer_ids(limit=1, page=2)

        # Then
        assert len(offer_ids) == 1
        assert (offer4.id,) in offer_ids
        assert (offer1.id,) not in offer_ids
        assert (offer2.id,) not in offer_ids
        assert (offer3.id,) not in offer_ids


class GetPaginatedOfferIdsByVenueIdTest:
    @pytest.mark.usefixtures("db_session")
    def test_should_return_one_offer_id_in_two_offers_from_first_page_when_limit_is_one(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer=offerer)
        offer1 = create_offer_with_event_product(venue=venue)
        offer2 = create_offer_with_event_product(venue=venue)
        repository.save(offer1, offer2)

        # When
        offer_ids = get_paginated_offer_ids_by_venue_id(venue_id=venue.id, limit=1, page=0)

        # Then
        assert len(offer_ids) == 1
        assert (offer1.id,) in offer_ids
        assert (offer2.id,) not in offer_ids

    @pytest.mark.usefixtures("db_session")
    def test_should_return_one_offer_id_in_two_offers_from_second_page_when_limit_is_one(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer=offerer)
        offer1 = create_offer_with_event_product(venue=venue)
        offer2 = create_offer_with_event_product(venue=venue)
        repository.save(offer1, offer2)

        # When
        offer_ids = get_paginated_offer_ids_by_venue_id(venue_id=venue.id, limit=1, page=1)

        # Then
        assert len(offer_ids) == 1
        assert (offer2.id,) in offer_ids
        assert (offer1.id,) not in offer_ids
