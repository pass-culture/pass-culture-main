from datetime import datetime
from datetime import timedelta

import pytest
from sqlalchemy import func

import pcapi.core.offers.factories as offers_factories
from pcapi.model_creators.generic_creators import create_booking
from pcapi.model_creators.generic_creators import create_offerer
from pcapi.model_creators.generic_creators import create_provider
from pcapi.model_creators.generic_creators import create_user
from pcapi.model_creators.generic_creators import create_user_offerer
from pcapi.model_creators.generic_creators import create_venue
from pcapi.model_creators.specific_creators import create_event_occurrence
from pcapi.model_creators.specific_creators import create_offer_with_event_product
from pcapi.model_creators.specific_creators import create_offer_with_thing_product
from pcapi.model_creators.specific_creators import create_product_with_event_type
from pcapi.model_creators.specific_creators import create_product_with_thing_type
from pcapi.model_creators.specific_creators import create_stock_from_event_occurrence
from pcapi.model_creators.specific_creators import create_stock_from_offer
from pcapi.models import Offer
from pcapi.models import Product
from pcapi.models import StockSQLEntity
from pcapi.models.offer_type import EventType
from pcapi.models.offer_type import ThingType
from pcapi.repository import repository
from pcapi.repository.offer_queries import _build_bookings_quantity_subquery
from pcapi.repository.offer_queries import department_or_national_offers
from pcapi.repository.offer_queries import find_activation_offers
from pcapi.repository.offer_queries import get_all_offers_id_by_filters
from pcapi.repository.offer_queries import get_offers_by_ids
from pcapi.repository.offer_queries import get_offers_by_venue_id
from pcapi.repository.offer_queries import get_paginated_active_offer_ids
from pcapi.repository.offer_queries import get_paginated_offer_ids_by_venue_id
from pcapi.repository.offer_queries import get_paginated_offer_ids_by_venue_id_and_last_provider_id
from pcapi.repository.offer_queries import get_paginated_offer_ids_given_booking_limit_datetime_interval
from pcapi.repository.offer_queries import update_offers_is_active_status
from pcapi.utils.converter import from_tuple_to_int


class DepartmentOrNationalOffersTest:
    @pytest.mark.usefixtures("db_session")
    def test_returns_national_thing_with_different_department(self, app):
        # given
        product = create_product_with_thing_type(thing_name='Lire un livre', is_national=True)
        offerer = create_offerer()
        venue = create_venue(offerer, postal_code='34000', departement_code='34')
        offer = create_offer_with_thing_product(venue=venue, product=product)
        repository.save(offer)
        query = Product.query.filter_by(name='Lire un livre')

        # when
        query = department_or_national_offers(query, ['93'])

        # then
        assert product in query.all()

    @pytest.mark.usefixtures("db_session")
    def test_returns_national_event_with_different_department(self, app):
        # given
        product = create_product_with_event_type('Voir une pièce', is_national=True)
        offerer = create_offerer()
        venue = create_venue(offerer, is_virtual=False, postal_code='29000', departement_code='29')
        offer = create_offer_with_event_product(venue=venue, product=product)
        repository.save(offer)
        query = Product.query.filter_by(name='Voir une pièce')

        # when
        query = department_or_national_offers(query, ['93'])

        # then
        assert product in query.all()

    @pytest.mark.usefixtures("db_session")
    def test_returns_nothing_if_event_is_not_in_given_department_list(self, app):
        # given
        product = create_product_with_event_type('Voir une pièce', is_national=False)
        offerer = create_offerer()
        venue = create_venue(offerer, is_virtual=False, postal_code='29000', departement_code='29')
        offer = create_offer_with_event_product(venue=venue, product=product)
        repository.save(offer)
        query = Product.query.filter_by(name='Voir une pièce')

        # when
        query = department_or_national_offers(query, ['34'])

        # then
        assert query.count() == 0

    @pytest.mark.usefixtures("db_session")
    def test_returns_an_event_regardless_of_department_if_department_list_contains_00(self, app):
        # given
        product = create_product_with_event_type('Voir une pièce', is_national=False)
        offerer = create_offerer()
        venue = create_venue(offerer, is_virtual=False, postal_code='29000', departement_code='29')
        offer = create_offer_with_event_product(venue=venue, product=product)
        repository.save(offer)
        query = Product.query.filter_by(name='Voir une pièce')

        # when
        query = department_or_national_offers(query, ['00'])

        # then
        assert query.count() == 1

    @pytest.mark.usefixtures("db_session")
    def test_returns_an_event_if_it_is_given_in_department_list(self, app):
        # given
        product = create_product_with_event_type('Voir une pièce', is_national=False)
        offerer = create_offerer()
        venue = create_venue(offerer, is_virtual=False, postal_code='29000', departement_code='29')
        offer = create_offer_with_event_product(venue=venue, product=product)
        repository.save(offer)
        query = Product.query.filter_by(name='Voir une pièce')

        # when
        query = department_or_national_offers(query, ['29'])

        # then
        assert query.count() == 1


class FindActivationOffersTest:
    @pytest.mark.usefixtures("db_session")
    def test_find_activation_offers_returns_activation_offers_in_given_department(self, app):
        # given
        offerer = create_offerer(siren='123456789')
        venue1 = create_venue(offerer, siret=offerer.siren + '12345', postal_code='34000', departement_code='34')
        venue2 = create_venue(offerer, siret=offerer.siren + '54321', postal_code='93000', departement_code='93')
        offer1 = create_offer_with_event_product(venue1, event_type=EventType.ACTIVATION)
        offer2 = create_offer_with_event_product(venue1, event_type=EventType.SPECTACLE_VIVANT)
        offer3 = create_offer_with_event_product(venue2, event_type=EventType.ACTIVATION)
        stock1 = create_stock_from_offer(offer1)
        stock2 = create_stock_from_offer(offer2)
        stock3 = create_stock_from_offer(offer3)
        repository.save(stock1, stock2, stock3)

        # when
        offers = find_activation_offers('34').all()

        # then
        assert len(offers) == 1

    @pytest.mark.usefixtures("db_session")
    def test_find_activation_offers_returns_activation_offers_if_offer_is_national(self, app):
        # given
        offerer = create_offerer(siren='123456789')
        venue1 = create_venue(offerer, siret=offerer.siren + '12345', postal_code='34000', departement_code='34')
        venue2 = create_venue(offerer, siret=offerer.siren + '54321', postal_code='93000', departement_code='93')
        offer1 = create_offer_with_event_product(venue1, event_type=EventType.ACTIVATION)
        offer2 = create_offer_with_thing_product(venue=venue1, thing_type=ThingType.AUDIOVISUEL)
        offer3 = create_offer_with_event_product(venue2, event_type=EventType.ACTIVATION, is_national=True)
        offer4 = create_offer_with_event_product(venue2, event_type=EventType.ACTIVATION, is_national=True)
        stock1 = create_stock_from_offer(offer1)
        stock2 = create_stock_from_offer(offer2)
        stock3 = create_stock_from_offer(offer3)
        stock4 = create_stock_from_offer(offer4)
        repository.save(stock1, stock2, stock3, stock4)

        # when
        offers = find_activation_offers('34').all()

        # then
        assert len(offers) == 3

    @pytest.mark.usefixtures("db_session")
    def test_find_activation_offers_returns_activation_offers_in_all_ile_de_france_if_department_is_93(self, app):
        # given
        offerer = create_offerer(siren='123456789')
        venue1 = create_venue(offerer, siret=offerer.siren + '12345', postal_code='34000', departement_code='34')
        venue2 = create_venue(offerer, siret=offerer.siren + '67890', postal_code='75000', departement_code='75')
        venue3 = create_venue(offerer, siret=offerer.siren + '54321', postal_code='78000', departement_code='78')
        offer1 = create_offer_with_event_product(venue1, event_type=EventType.ACTIVATION)
        offer2 = create_offer_with_event_product(venue2, event_type=EventType.ACTIVATION)
        offer3 = create_offer_with_event_product(venue3, event_type=EventType.ACTIVATION)
        stock1 = create_stock_from_offer(offer1)
        stock2 = create_stock_from_offer(offer2)
        stock3 = create_stock_from_offer(offer3)
        repository.save(stock1, stock2, stock3)

        # when
        offers = find_activation_offers('93').all()

        # then
        assert len(offers) == 2

    @pytest.mark.usefixtures("db_session")
    def test_find_activation_offers_returns_activation_offers_with_available_stocks(self, app):
        # given
        user = create_user()
        offerer = create_offerer(siren='123456789')
        venue1 = create_venue(offerer=offerer, siret=offerer.siren + '12345', postal_code='93000',
                              departement_code='93')
        venue2 = create_venue(offerer=offerer, siret=offerer.siren + '67890', postal_code='93000',
                              departement_code='93')
        venue3 = create_venue(offerer=offerer, siret=offerer.siren + '54321', postal_code='93000',
                              departement_code='93')
        offer1 = create_offer_with_event_product(venue=venue1, event_type=EventType.ACTIVATION)
        offer2 = create_offer_with_event_product(venue=venue2, event_type=EventType.ACTIVATION)
        offer3 = create_offer_with_event_product(venue=venue3, event_type=EventType.ACTIVATION)
        offer4 = create_offer_with_event_product(venue=venue3, event_type=EventType.ACTIVATION)
        stock1 = create_stock_from_offer(offer1, price=0, quantity=0)
        stock2 = create_stock_from_offer(offer2, price=0, quantity=10)
        stock3 = create_stock_from_offer(offer3, price=0, quantity=1)
        booking = create_booking(user=user, stock=stock3, quantity=1, venue=venue3)
        repository.save(stock1, stock2, stock3, booking, offer4)

        # when
        offers = find_activation_offers('93').all()

        # then
        assert len(offers) == 1

    @pytest.mark.usefixtures("db_session")
    def test_find_activation_offers_returns_activation_offers_with_future_booking_limit_datetime(self, app):
        # given
        now = datetime.utcnow()
        five_days_ago = now - timedelta(days=5)
        next_week = now + timedelta(days=7)
        offerer = create_offerer(siren='123456789')
        venue1 = create_venue(offerer, siret=offerer.siren + '12345', postal_code='93000', departement_code='93')
        venue2 = create_venue(offerer, siret=offerer.siren + '67890', postal_code='93000', departement_code='93')
        venue3 = create_venue(offerer, siret=offerer.siren + '54321', postal_code='93000', departement_code='93')
        offer1 = create_offer_with_event_product(venue=venue1, event_type=EventType.ACTIVATION)
        offer2 = create_offer_with_event_product(venue=venue2, event_type=EventType.ACTIVATION)
        offer3 = create_offer_with_event_product(venue=venue3, event_type=EventType.ACTIVATION)
        stock1 = create_stock_from_offer(offer=offer1, price=0, booking_limit_datetime=five_days_ago)
        stock2 = create_stock_from_offer(offer=offer2, price=0, booking_limit_datetime=next_week)
        stock3 = create_stock_from_offer(offer=offer3, price=0, booking_limit_datetime=None)
        repository.save(stock1, stock2, stock3)

        # when
        offers = find_activation_offers('93').all()

        # then
        assert offer1 not in offers
        assert offer2 in offers
        assert offer3 in offers


class FindOffersTest:
    @pytest.mark.usefixtures("db_session")
    def test_get_offers_by_venue_id_returns_offers_matching_venue_id(self, app):
        # Given
        product = create_product_with_thing_type(thing_name='Lire un livre', is_national=True)
        offerer = create_offerer()
        venue = create_venue(offerer, postal_code='34000', departement_code='34')
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
        user = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue=venue, product=thing)
        repository.save(offer)

        # When
        offers_count = Offer.query \
            .join(StockSQLEntity) \
            .count()

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
        offers_count = Offer.query \
            .join(StockSQLEntity) \
            .outerjoin(bookings_quantity, StockSQLEntity.id == bookings_quantity.c.stockId) \
            .filter((StockSQLEntity.quantity == None) | (
                (StockSQLEntity.quantity - func.coalesce(bookings_quantity.c.quantity, 0)) > 0)) \
            .count()

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
        offers_count = Offer.query \
            .join(StockSQLEntity) \
            .outerjoin(bookings_quantity, StockSQLEntity.id == bookings_quantity.c.stockId) \
            .filter((StockSQLEntity.quantity == None) | (
                (StockSQLEntity.quantity - func.coalesce(bookings_quantity.c.quantity, 0)) > 0)) \
            .count()

        # Then
        assert offers_count == 0

    @pytest.mark.usefixtures("db_session")
    def test_should_return_1_offer_when_booking_was_cancelled(self, app):
        # Given
        user = create_user()
        product = create_product_with_thing_type(thing_name='Lire un livre', is_national=True)
        offerer = create_offerer()
        venue = create_venue(offerer, postal_code='34000', departement_code='34')
        offer = create_offer_with_thing_product(venue=venue, product=product)
        stock = create_stock_from_offer(offer, quantity=2)
        booking = create_booking(user=user, stock=stock, is_cancelled=True, quantity=2, venue=venue)
        repository.save(booking)
        bookings_quantity = _build_bookings_quantity_subquery()

        # When
        offers_count = Offer.query \
            .join(StockSQLEntity) \
            .outerjoin(bookings_quantity, StockSQLEntity.id == bookings_quantity.c.stockId) \
            .filter((StockSQLEntity.quantity == None) | (
                (StockSQLEntity.quantity - func.coalesce(bookings_quantity.c.quantity, 0)) > 0)) \
            .count()

        # Then
        assert offers_count == 1

    @pytest.mark.usefixtures("db_session")
    def test_should_return_0_offer_when_there_is_no_remaining_stock(app):
        # Given
        product = create_product_with_thing_type(thing_name='Lire un livre', is_national=True)
        offerer = create_offerer()
        venue = create_venue(offerer, postal_code='34000', departement_code='34')
        offer = create_offer_with_thing_product(venue=venue, product=product)
        stock = create_stock_from_offer(offer, price=0, quantity=2)
        user = create_user()
        booking1 = create_booking(user=user, stock=stock, is_cancelled=True, quantity=2, venue=venue)
        booking2 = create_booking(user=user, stock=stock, quantity=2, venue=venue)
        repository.save(booking1, booking2)
        bookings_quantity = _build_bookings_quantity_subquery()

        # When
        offers_count = Offer.query \
            .join(StockSQLEntity) \
            .outerjoin(bookings_quantity, StockSQLEntity.id == bookings_quantity.c.stockId) \
            .filter((StockSQLEntity.quantity == None) | (
                (StockSQLEntity.quantity - func.coalesce(bookings_quantity.c.quantity, 0)) > 0)) \
            .count()

        # Then
        assert offers_count == 0

    @pytest.mark.usefixtures("db_session")
    def test_should_return_1_offer_when_there_are_one_full_stock_and_one_empty_stock(app):
        # Given
        product = create_product_with_thing_type(thing_name='Lire un livre', is_national=True)
        offerer = create_offerer()
        venue = create_venue(offerer, postal_code='34000', departement_code='34')
        offer = create_offer_with_thing_product(venue=venue, product=product)
        stock1 = create_stock_from_offer(offer, price=0, quantity=2)
        stock2 = create_stock_from_offer(offer, price=0, quantity=2)
        user = create_user()
        booking1 = create_booking(user=user, stock=stock1, quantity=2, venue=venue)
        repository.save(booking1, stock2)
        bookings_quantity = _build_bookings_quantity_subquery()

        # When
        offers_count = Offer.query \
            .join(StockSQLEntity) \
            .outerjoin(bookings_quantity, StockSQLEntity.id == bookings_quantity.c.stockId) \
            .filter((StockSQLEntity.quantity == None) | (
                (StockSQLEntity.quantity - func.coalesce(bookings_quantity.c.quantity, 0)) > 0)) \
            .count()

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


class GetPaginatedOfferIdsByVenueIdAndLastProviderIdTest:
    @pytest.mark.usefixtures("db_session")
    def test_should_return_offer_ids_when_exist_and_venue_id_and_last_provider_id_match(self, app):
        # Given
        provider1 = create_provider(idx=1, local_class='OpenAgenda', is_active=False, is_enable_for_pro=False)
        provider2 = create_provider(idx=2, local_class='TiteLive', is_active=False, is_enable_for_pro=False)
        offerer = create_offerer()
        venue = create_venue(offerer=offerer)
        offer1 = create_offer_with_thing_product(last_provider_id=provider1.id, venue=venue, last_provider=provider1)
        offer2 = create_offer_with_thing_product(last_provider_id=provider2.id, venue=venue, last_provider=provider2)
        repository.save(provider1, provider2, offer1, offer2)

        # When
        offer_ids = get_paginated_offer_ids_by_venue_id_and_last_provider_id(last_provider_id=provider1.id,
                                                                             limit=2,
                                                                             page=0,
                                                                             venue_id=venue.id)

        # Then
        assert len(offer_ids) == 1
        assert offer_ids[0] == (offer1.id,)

    @pytest.mark.usefixtures("db_session")
    def test_should_return_one_offer_id_when_exist_and_venue_id_and_last_provider_id_match_from_first_page_only(self,
                                                                                                                app):
        # Given
        provider1 = create_provider(idx=1, local_class='OpenAgenda', is_active=False, is_enable_for_pro=False)
        offerer = create_offerer()
        venue = create_venue(offerer=offerer)
        offer1 = create_offer_with_thing_product(last_provider_id=provider1.id, venue=venue, last_provider=provider1)
        offer2 = create_offer_with_thing_product(last_provider_id=provider1.id, venue=venue, last_provider=provider1)
        repository.save(provider1, offer1, offer2)

        # When
        offer_ids = get_paginated_offer_ids_by_venue_id_and_last_provider_id(last_provider_id=provider1.id,
                                                                             limit=1,
                                                                             page=0,
                                                                             venue_id=venue.id)

        # Then
        assert len(offer_ids) == 1
        assert offer_ids[0] == (offer1.id,)

    @pytest.mark.usefixtures("db_session")
    def test_should_return_one_offer_id_when_exist_and_venue_id_and_last_provider_id_match_from_second_page_only(self,
                                                                                                                 app):
        # Given
        provider1 = create_provider(idx=1, local_class='OpenAgenda', is_active=False, is_enable_for_pro=False)
        offerer = create_offerer()
        venue = create_venue(offerer=offerer)
        offer1 = create_offer_with_thing_product(last_provider_id=provider1.id, venue=venue, last_provider=provider1)
        offer2 = create_offer_with_thing_product(last_provider_id=provider1.id, venue=venue, last_provider=provider1)
        repository.save(provider1, offer1, offer2)

        # When
        offer_ids = get_paginated_offer_ids_by_venue_id_and_last_provider_id(last_provider_id=provider1.id,
                                                                             limit=1,
                                                                             page=1,
                                                                             venue_id=venue.id)

        # Then
        assert len(offer_ids) == 1
        assert offer_ids[0] == (offer2.id,)

    @pytest.mark.usefixtures("db_session")
    def test_should_not_return_offer_ids_when_venue_id_and_last_provider_id_do_not_match(self, app):
        # Given
        provider1 = create_provider(idx=1, local_class='OpenAgenda', is_active=False, is_enable_for_pro=False)
        provider2 = create_provider(idx=2, local_class='TiteLive', is_active=False, is_enable_for_pro=False)
        offerer = create_offerer()
        venue = create_venue(offerer=offerer)
        offer1 = create_offer_with_thing_product(last_provider_id=provider1.id, venue=venue)
        offer2 = create_offer_with_thing_product(last_provider_id=provider2.id, venue=venue)
        repository.save(provider1, provider2, offer1, offer2)

        # When
        offer_ids = get_paginated_offer_ids_by_venue_id_and_last_provider_id(last_provider_id='3',
                                                                             limit=2,
                                                                             page=0,
                                                                             venue_id=10)

        # Then
        assert len(offer_ids) == 0

    @pytest.mark.usefixtures("db_session")
    def test_should_not_return_offer_ids_when_venue_id_matches_but_last_provider_id_do_not_match(self, app):
        # Given
        provider1 = create_provider(idx=1, local_class='OpenAgenda', is_active=False, is_enable_for_pro=False)
        provider2 = create_provider(idx=2, local_class='TiteLive', is_active=False, is_enable_for_pro=False)
        offerer = create_offerer()
        venue = create_venue(offerer=offerer)
        offer1 = create_offer_with_thing_product(last_provider_id=provider1.id, venue=venue)
        offer2 = create_offer_with_thing_product(last_provider_id=provider2.id, venue=venue)
        repository.save(provider1, provider2, offer1, offer2)

        # When
        offer_ids = get_paginated_offer_ids_by_venue_id_and_last_provider_id(last_provider_id='3',
                                                                             limit=2,
                                                                             page=0,
                                                                             venue_id=venue.id)

        # Then
        assert len(offer_ids) == 0

    @pytest.mark.usefixtures("db_session")
    def test_should_not_return_offer_ids_when_venue_id_do_not_matches_but_last_provider_id_matches(self, app):
        # Given
        provider1 = create_provider(idx=1, local_class='OpenAgenda', is_active=False, is_enable_for_pro=False)
        provider2 = create_provider(idx=2, local_class='TiteLive', is_active=False, is_enable_for_pro=False)
        offerer = create_offerer()
        venue = create_venue(offerer=offerer)
        offer1 = create_offer_with_thing_product(last_provider_id=provider1.id, venue=venue)
        offer2 = create_offer_with_thing_product(last_provider_id=provider2.id, venue=venue)
        repository.save(provider1, provider2, offer1, offer2)

        # When
        offer_ids = get_paginated_offer_ids_by_venue_id_and_last_provider_id(last_provider_id=provider1.id,
                                                                             limit=2,
                                                                             page=0,
                                                                             venue_id=10)

        # Then
        assert len(offer_ids) == 0


class GetPaginatedOfferIdsGivenBookingLimitDatetimeIntervalTest:
    @pytest.mark.usefixtures("db_session")
    def test_should_return_one_offer_id_from_first_page_when_active_and_booking_limit_datetime_is_expired(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer=offerer)
        offer1 = create_offer_with_event_product(is_active=True, venue=venue)
        offer2 = create_offer_with_event_product(is_active=True, venue=venue)
        offer3 = create_offer_with_thing_product(is_active=True, venue=venue)
        offer4 = create_offer_with_thing_product(is_active=True, venue=venue)
        stock1 = create_stock_from_offer(offer=offer1, booking_limit_datetime=datetime(2019, 12, 31, 0, 0, 0))
        stock2 = create_stock_from_offer(offer=offer2, booking_limit_datetime=datetime(2019, 1, 1, 0, 0, 0))
        stock3 = create_stock_from_offer(offer=offer3, booking_limit_datetime=datetime(2020, 1, 2, 0, 0, 0))
        stock4 = create_stock_from_offer(offer=offer4, booking_limit_datetime=datetime(2020, 1, 3, 0, 0, 0))
        repository.save(stock1, stock2, stock3, stock4)

        # When
        results = get_paginated_offer_ids_given_booking_limit_datetime_interval(
            limit=1,
            page=0,
            from_date=datetime(2019, 12, 30, 10, 0, 0),
            to_date=datetime(2019, 12, 31, 10, 0, 0)
        )

        # Then
        assert len(results) == 1
        assert (offer1.id,) in results
        assert (offer2.id,) not in results
        assert (offer3.id,) not in results
        assert (offer4.id,) not in results

    @pytest.mark.usefixtures("db_session")
    def test_should_return_two_offer_ids_from_second_page_when_active_and_booking_limit_datetime_is_expired(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer=offerer)
        offer1 = create_offer_with_event_product(is_active=True, venue=venue)
        offer2 = create_offer_with_event_product(is_active=True, venue=venue)
        offer3 = create_offer_with_thing_product(is_active=True, venue=venue)
        offer4 = create_offer_with_thing_product(is_active=True, venue=venue)
        stock1 = create_stock_from_offer(offer=offer1, booking_limit_datetime=datetime(2019, 12, 31, 0, 0, 0))
        stock2 = create_stock_from_offer(offer=offer2, booking_limit_datetime=datetime(2019, 12, 31, 0, 0, 0))
        stock3 = create_stock_from_offer(offer=offer3, booking_limit_datetime=datetime(2019, 12, 31, 0, 0, 0))
        stock4 = create_stock_from_offer(offer=offer4, booking_limit_datetime=datetime(2019, 12, 31, 0, 0, 0))
        repository.save(stock1, stock2, stock3, stock4)

        # When
        results = get_paginated_offer_ids_given_booking_limit_datetime_interval(
            limit=2,
            page=1,
            from_date=datetime(2019, 12, 30, 10, 0, 0),
            to_date=datetime(2019, 12, 31, 10, 0, 0)
        )

        # Then
        assert len(results) == 2
        assert (offer1.id,) not in results
        assert (offer2.id,) not in results
        assert (offer3.id,) in results
        assert (offer4.id,) in results

    @pytest.mark.usefixtures("db_session")
    def test_should_not_return_offer_ids_when_not_active_and_booking_limit_datetime_is_expired(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer=offerer)
        offer1 = create_offer_with_event_product(is_active=False, venue=venue)
        offer2 = create_offer_with_event_product(is_active=False, venue=venue)
        offer3 = create_offer_with_thing_product(is_active=False, venue=venue)
        offer4 = create_offer_with_thing_product(is_active=False, venue=venue)
        stock1 = create_stock_from_offer(offer=offer1, booking_limit_datetime=datetime(2019, 12, 21, 0, 0, 0))
        stock2 = create_stock_from_offer(offer=offer2, booking_limit_datetime=datetime(2019, 12, 22, 0, 0, 0))
        stock3 = create_stock_from_offer(offer=offer3, booking_limit_datetime=datetime(2019, 12, 23, 0, 0, 0))
        stock4 = create_stock_from_offer(offer=offer4, booking_limit_datetime=datetime(2019, 12, 24, 0, 0, 0))
        repository.save(stock1, stock2, stock3, stock4)

        # When
        results = get_paginated_offer_ids_given_booking_limit_datetime_interval(
            limit=4,
            page=0,
            from_date=datetime(2019, 12, 30, 10, 0, 0),
            to_date=datetime(2019, 12, 31, 10, 0, 0)
        )

        # Then
        assert len(results) == 0

    @pytest.mark.usefixtures("db_session")
    def test_should_not_return_offer_ids_when_active_and_booking_limit_datetime_is_not_expired(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer=offerer)
        offer1 = create_offer_with_event_product(is_active=True, venue=venue)
        offer2 = create_offer_with_event_product(is_active=True, venue=venue)
        offer3 = create_offer_with_thing_product(is_active=True, venue=venue)
        offer4 = create_offer_with_thing_product(is_active=True, venue=venue)
        stock1 = create_stock_from_offer(offer=offer1, booking_limit_datetime=datetime(2020, 1, 2, 0, 0, 0))
        stock2 = create_stock_from_offer(offer=offer2, booking_limit_datetime=datetime(2020, 1, 2, 0, 0, 0))
        stock3 = create_stock_from_offer(offer=offer3, booking_limit_datetime=datetime(2020, 1, 2, 0, 0, 0))
        stock4 = create_stock_from_offer(offer=offer4, booking_limit_datetime=datetime(2020, 1, 2, 0, 0, 0))
        repository.save(stock1, stock2, stock3, stock4)

        # When
        results = get_paginated_offer_ids_given_booking_limit_datetime_interval(
            limit=4,
            page=0,
            from_date=datetime(2019, 12, 30, 10, 0, 0),
            to_date=datetime(2019, 12, 31, 10, 0, 0)
        )

        # Then
        assert len(results) == 0

    @pytest.mark.usefixtures("db_session")
    def test_should_return_one_offer_id_from_first_page_when_active_and_beginning_datetime_is_null(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer=offerer)
        offer1 = create_offer_with_event_product(is_active=True, venue=venue)
        offer2 = create_offer_with_event_product(is_active=True, venue=venue)
        offer3 = create_offer_with_thing_product(is_active=True, venue=venue)
        offer4 = create_offer_with_thing_product(is_active=True, venue=venue)
        stock1 = create_stock_from_offer(offer=offer1, booking_limit_datetime=datetime(2019, 12, 31, 0, 0, 0))
        stock2 = create_stock_from_offer(offer=offer2, booking_limit_datetime=datetime(2019, 12, 30, 0, 0, 0))
        stock3 = create_stock_from_offer(offer=offer3, booking_limit_datetime=datetime(2020, 1, 2, 0, 0, 0),
                                         beginning_datetime=None)
        stock4 = create_stock_from_offer(offer=offer4, booking_limit_datetime=datetime(2020, 1, 3, 0, 0, 0),
                                         beginning_datetime=None)
        repository.save(stock1, stock2, stock3, stock4)

        # When
        results = get_paginated_offer_ids_given_booking_limit_datetime_interval(
            limit=1,
            page=0,
            from_date=datetime(2019, 12, 30, 10, 0, 0),
            to_date=datetime(2019, 12, 31, 10, 0, 0)
        )

        # Then
        assert len(results) == 1
        assert (offer1.id,) in results
        assert (offer2.id,) not in results
        assert (offer3.id,) not in results
        assert (offer4.id,) not in results

    @pytest.mark.usefixtures("db_session")
    def test_should_return_one_offer_id_when_two_offers_are_expired_and_the_second_one_is_out_of_range(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer=offerer)
        offer1 = create_offer_with_event_product(is_active=True, venue=venue)
        offer2 = create_offer_with_event_product(is_active=True, venue=venue)
        in_range_stock = create_stock_from_offer(offer=offer1, booking_limit_datetime=datetime(2019, 12, 31, 0, 0, 0))
        out_of_range_stock = create_stock_from_offer(offer=offer2,
                                                     booking_limit_datetime=datetime(2019, 12, 1, 0, 0, 0))
        repository.save(in_range_stock, out_of_range_stock)

        # When
        results = get_paginated_offer_ids_given_booking_limit_datetime_interval(
            limit=2,
            page=0,
            from_date=datetime(2019, 12, 30, 10, 0, 0),
            to_date=datetime(2019, 12, 31, 10, 0, 0)
        )

        # Then
        assert len(results) == 1
        assert (offer1.id,) in results
        assert (offer2.id,) not in results

    @pytest.mark.usefixtures("db_session")
    def test_should_return_no_offer_ids_when_offers_are_expired_since_more_than_two_days(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer=offerer)
        offer1 = create_offer_with_event_product(is_active=True, venue=venue)
        offer2 = create_offer_with_event_product(is_active=True, venue=venue)
        out_of_range_stock1 = create_stock_from_offer(offer=offer1,
                                                      booking_limit_datetime=datetime(2019, 12, 30, 9, 59, 0))
        out_of_range_stock2 = create_stock_from_offer(offer=offer2,
                                                      booking_limit_datetime=datetime(2019, 12, 29, 0, 0, 0))
        repository.save(out_of_range_stock1, out_of_range_stock2)

        # When
        results = get_paginated_offer_ids_given_booking_limit_datetime_interval(
            limit=2,
            page=0,
            from_date=datetime(2019, 12, 30, 10, 0, 0),
            to_date=datetime(2019, 12, 31, 10, 0, 0)
        )

        # Then
        assert len(results) == 0

    @pytest.mark.usefixtures("db_session")
    def test_should_return_one_offer_id_when_offers_are_expired_since_more_than_two_days_and_one_second(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer=offerer)
        offer1 = create_offer_with_event_product(is_active=True, venue=venue)
        offer2 = create_offer_with_event_product(is_active=True, venue=venue)
        in_range_stock = create_stock_from_offer(offer=offer1, booking_limit_datetime=datetime(2019, 12, 30, 10, 1, 0))
        out_of_range_stock = create_stock_from_offer(offer=offer2,
                                                     booking_limit_datetime=datetime(2019, 12, 30, 9, 59, 59))
        repository.save(in_range_stock, out_of_range_stock)

        # When
        results = get_paginated_offer_ids_given_booking_limit_datetime_interval(
            limit=2,
            page=0,
            from_date=datetime(2019, 12, 30, 10, 0, 0),
            to_date=datetime(2019, 12, 31, 10, 0, 0)
        )

        # Then
        assert len(results) == 1
        assert offer1 in results
        assert offer2 not in results

    @pytest.mark.usefixtures("db_session")
    def test_should_return_one_offer_id_when_offers_are_expired_exactly_since_two_days(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer=offerer)
        offer1 = create_offer_with_event_product(is_active=True, venue=venue)
        offer2 = create_offer_with_event_product(is_active=True, venue=venue)
        in_range_stock = create_stock_from_offer(offer=offer1, booking_limit_datetime=datetime(2019, 12, 30, 10, 0, 0))
        out_of_range_stock = create_stock_from_offer(offer=offer2,
                                                     booking_limit_datetime=datetime(2019, 12, 30, 9, 59, 59))
        repository.save(in_range_stock, out_of_range_stock)

        # When
        results = get_paginated_offer_ids_given_booking_limit_datetime_interval(
            limit=2,
            page=0,
            from_date=datetime(2019, 12, 30, 10, 0, 0),
            to_date=datetime(2019, 12, 31, 10, 0, 0)
        )

        # Then
        assert len(results) == 1
        assert offer1 in results
        assert offer2 not in results

    @pytest.mark.usefixtures("db_session")
    def test_should_return_one_offer_id_when_offers_are_expired_exactly_since_one_day(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer=offerer)
        offer1 = create_offer_with_event_product(is_active=True, venue=venue)
        offer2 = create_offer_with_event_product(is_active=True, venue=venue)
        in_range_stock = create_stock_from_offer(offer=offer1, booking_limit_datetime=datetime(2019, 12, 31, 10, 0, 0))
        out_of_range_stock = create_stock_from_offer(offer=offer2,
                                                     booking_limit_datetime=datetime(2019, 12, 30, 9, 59, 59))
        repository.save(in_range_stock, out_of_range_stock)

        # When
        results = get_paginated_offer_ids_given_booking_limit_datetime_interval(
            limit=2,
            page=0,
            from_date=datetime(2019, 12, 30, 10, 0, 0),
            to_date=datetime(2019, 12, 31, 10, 0, 0)
        )

        # Then
        assert len(results) == 1
        assert offer1 in results
        assert offer2 not in results

    @pytest.mark.usefixtures("db_session")
    def should_not_get_offer_with_valid_stocks(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer=offerer)
        offer = create_offer_with_event_product(is_active=True, venue=venue)
        expired_stock = create_stock_from_offer(offer=offer,
                                                booking_limit_datetime=datetime(2019, 12, 31))
        valid_stock = create_stock_from_offer(offer=offer,
                                              booking_limit_datetime=datetime(2020, 1, 30))
        repository.save(expired_stock, valid_stock)

        # When
        results = get_paginated_offer_ids_given_booking_limit_datetime_interval(
            limit=2,
            page=0,
            from_date=datetime(2019, 12, 30, 10, 0, 0),
            to_date=datetime(2019, 12, 31, 10, 0, 0)
        )

        # Then
        assert results == []

    @pytest.mark.usefixtures("db_session")
    def should_ignore_soft_deleted_stocks(self, app):
        offer = offers_factories.OfferFactory()
        offers_factories.StockFactory(
            offer=offer,
            bookingLimitDatetime=datetime(2019, 12, 31),  # within range
        )
        offers_factories.StockFactory(
            offer=offer,
            bookingLimitDatetime=datetime(2020, 1, 31),  # in the future
            isSoftDeleted=True,
        )

        expired_offer_ids = get_paginated_offer_ids_given_booking_limit_datetime_interval(
            limit=1,
            page=0,
            from_date=datetime(2019, 12, 30, 10, 0, 0),
            to_date=datetime(2019, 12, 31, 10, 0, 0)
        )

        # Then
        expired_offer_ids = from_tuple_to_int(expired_offer_ids)
        assert expired_offer_ids == [offer.id]


class UpdateOffersIsActiveStatusTest:
    @pytest.mark.usefixtures("db_session")
    def should_update_is_active_status_for_given_offers_id_and_status(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer=offerer)
        offer1 = create_offer_with_thing_product(venue=venue, is_active=False)
        offer2 = create_offer_with_thing_product(venue=venue, is_active=False)
        offer3 = create_offer_with_thing_product(venue=venue, is_active=False)
        repository.save(offer1, offer2, offer3)
        offers_id = [offer1.id, offer2.id]

        # When
        update_offers_is_active_status(offers_id=offers_id, is_active=True)

        # Then
        assert Offer.query.get(offer1.id).isActive == True
        assert Offer.query.get(offer2.id).isActive == True
        assert Offer.query.get(offer3.id).isActive == False

class GetAllOffersIdByFiltersTest:
    @pytest.mark.usefixtures("db_session")
    def test_should_return_all_offers_ids_filtered_by_given_params(self, app):
        # Given
        user = create_user()
        offerer = create_offerer()
        create_user_offerer(user, offerer)
        provider = create_provider()
        wanted_venue = create_venue(offerer=offerer)
        unwanted_venue = create_venue(offerer=offerer, siret='12345678912344')
        wanted_offer = create_offer_with_thing_product(venue=wanted_venue, thing_name='Wanted name', is_active=False, last_provider=provider, last_provider_id=provider.id)
        unwanted_offer2 = create_offer_with_thing_product(venue=wanted_venue, is_active=False)
        unwanted_offer3 = create_offer_with_thing_product(venue=wanted_venue)
        unwanted_offer4 = create_offer_with_thing_product(venue=unwanted_venue)
        repository.save(user, wanted_offer, unwanted_offer2, unwanted_offer3, unwanted_offer4)

        # When
        offers_id = get_all_offers_id_by_filters(
            user_id=user.id,
            user_is_admin=user.isAdmin,
            offerer_id=offerer.id,
            status='inactive',
            venue_id=wanted_venue.id,
            name_keywords='Wanted',
            creation_mode='imported',
        )

        # Then
        assert len(offers_id) == 1
        assert wanted_offer.id in offers_id
