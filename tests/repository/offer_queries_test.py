from datetime import datetime, timedelta

from freezegun import freeze_time
from sqlalchemy import func

from models import Offer, StockSQLEntity, Product
from models.offer_type import EventType, ThingType
from repository import repository
from repository.offer_queries import department_or_national_offers, \
    find_activation_offers, \
    build_find_offers_with_filter_parameters, \
    get_offers_by_venue_id, \
    get_paginated_active_offer_ids, \
    get_paginated_offer_ids_by_venue_id_and_last_provider_id, \
    get_paginated_offer_ids_by_venue_id, \
    get_offers_by_ids, \
    get_paginated_expired_offer_ids, \
    _build_bookings_quantity_subquery
from tests.conftest import clean_database
from tests.model_creators.generic_creators import create_booking, create_criterion, create_user, create_offerer, \
    create_venue, create_user_offerer, create_provider
from tests.model_creators.specific_creators import create_product_with_thing_type, create_offer_with_thing_product, \
    create_product_with_event_type, create_offer_with_event_product, create_event_occurrence, \
    create_stock_from_event_occurrence, create_stock_from_offer

REFERENCE_DATE = '2017-10-15 09:21:34'


class DepartmentOrNationalOffersTest:
    @clean_database
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

    @clean_database
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

    @clean_database
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

    @clean_database
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

    @clean_database
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
    @clean_database
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

    @clean_database
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

    @clean_database
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

    @clean_database
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

    @clean_database
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
    @clean_database
    def test_returns_offers_sorted_by_id_desc(self, app):
        # Given
        user = create_user()
        offerer = create_offerer()
        user_offerer = create_user_offerer(user, offerer)
        venue = create_venue(offerer)
        offer1 = create_offer_with_thing_product(venue)
        offer2 = create_offer_with_thing_product(venue)
        repository.save(user_offerer, offer1, offer2)

        # When
        offers = build_find_offers_with_filter_parameters(
            user_id=user.id,
            user_is_admin=user.isAdmin,
        ).all()

        # Then
        assert offers[0].id > offers[1].id

    @clean_database
    def test_find_offers_with_filter_parameters_with_partial_keywords_and_filter_by_venue(self, app):
        user = create_user()
        offerer1 = create_offerer(siren='123456789')
        offerer2 = create_offerer(siren='987654321')
        ko_offerer3 = create_offerer(siren='123456780')
        user_offerer1 = create_user_offerer(user=user, offerer=offerer1)
        user_offerer2 = create_user_offerer(user=user, offerer=offerer2)

        ok_product_event = create_product_with_event_type(event_name='Rencontre avec Jacques Martin')
        ok_product_thing = create_product_with_thing_type(thing_name='Rencontrez Jacques Chirac')
        event_product2 = create_product_with_event_type(event_name='Concert de contrebasse')
        thing1_product = create_product_with_thing_type(thing_name='Jacques la fripouille')
        thing2_product = create_product_with_thing_type(thing_name='Belle du Seigneur')
        offerer = create_offerer(siren='123456789')
        venue1 = create_venue(offerer=offerer1, name='Bataclan', city='Paris', siret=offerer.siren + '12345')
        venue2 = create_venue(offerer=offerer2, name='Librairie la Rencontre', city='Saint Denis',
                              siret=offerer.siren + '54321')
        ko_venue3 = create_venue(ko_offerer3, name='Une librairie du méchant concurrent gripsou', city='Saint Denis',
                                 siret=ko_offerer3.siren + '54321')
        ok_offer1 = create_offer_with_event_product(venue=venue1, product=ok_product_event)
        ok_offer2 = create_offer_with_thing_product(venue=venue1, product=ok_product_thing)
        ko_offer2 = create_offer_with_event_product(venue=venue1, product=event_product2)
        ko_offer3 = create_offer_with_thing_product(venue=ko_venue3, product=thing1_product)
        ko_offer4 = create_offer_with_thing_product(venue=venue2, product=thing2_product)
        repository.save(
            user_offerer1, user_offerer2, ko_offerer3,
            ok_offer1, ko_offer2, ko_offer3, ko_offer4
        )

        # when
        offers = build_find_offers_with_filter_parameters(
            user_id=user.id,
            user_is_admin=user.isAdmin,
            venue_id=venue1.id,
            keywords_string='Jacq Rencon'
        ).all()

        # then
        offers_id = [offer.id for offer in offers]
        assert ok_offer1.id in offers_id
        assert ok_offer2.id in offers_id
        assert ko_offer2.id not in offers_id
        assert ko_offer3.id not in offers_id
        assert ko_offer4.id not in offers_id

    @clean_database
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
    @clean_database
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

    @clean_database
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

    @clean_database
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

    @clean_database
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

    @clean_database
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

    @clean_database
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


class BaseScoreTest:

    @clean_database
    def test_order_by_base_score(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer, postal_code='34000', departement_code='34')

        criterion_negative = create_criterion(name='negative', score_delta=-1)
        criterion_positive = create_criterion(name='positive', score_delta=1)

        offer1 = create_offer_with_thing_product(venue=venue)
        offer2 = create_offer_with_thing_product(venue=venue)

        offer1.criteria = [criterion_negative]
        offer2.criteria = [criterion_negative, criterion_positive]

        repository.save(offer1, offer2)

        # When
        offers = Offer.query \
            .order_by(Offer.baseScore.desc()) \
            .all()

        # Then
        assert offers == [offer2, offer1]


def _create_event_stock_and_offer_for_date(venue, date):
    product = create_product_with_event_type()
    offer = create_offer_with_event_product(venue=venue, product=product)
    event_occurrence = create_event_occurrence(offer, beginning_datetime=date)
    stock = create_stock_from_event_occurrence(event_occurrence, booking_limit_date=date)
    return stock


class GetOffersByIdsTest:
    @clean_database
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
    @clean_database
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

    @clean_database
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

    @clean_database
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
    @clean_database
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

    @clean_database
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
    @clean_database
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

    @clean_database
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

    @clean_database
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

    @clean_database
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

    @clean_database
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

    @clean_database
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


@freeze_time('2020-01-01 10:00:00')
class GetPaginatedExpiredOfferIdsTest:
    @clean_database
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
        results = get_paginated_expired_offer_ids(limit=1, page=0)

        # Then
        assert len(results) == 1
        assert (offer1.id,) in results
        assert (offer2.id,) not in results
        assert (offer3.id,) not in results
        assert (offer4.id,) not in results

    @clean_database
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
        results = get_paginated_expired_offer_ids(limit=2, page=1)

        # Then
        assert len(results) == 2
        assert (offer1.id,) not in results
        assert (offer2.id,) not in results
        assert (offer3.id,) in results
        assert (offer4.id,) in results

    @clean_database
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
        results = get_paginated_expired_offer_ids(limit=4, page=0)

        # Then
        assert len(results) == 0

    @clean_database
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
        results = get_paginated_expired_offer_ids(limit=4, page=0)

        # Then
        assert len(results) == 0

    @clean_database
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
        results = get_paginated_expired_offer_ids(limit=1, page=0)

        # Then
        assert len(results) == 1
        assert (offer1.id,) in results
        assert (offer2.id,) not in results
        assert (offer3.id,) not in results
        assert (offer4.id,) not in results

    @clean_database
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
        results = get_paginated_expired_offer_ids(limit=2, page=0)

        # Then
        assert len(results) == 1
        assert (offer1.id,) in results
        assert (offer2.id,) not in results

    @clean_database
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
        results = get_paginated_expired_offer_ids(limit=2, page=0)

        # Then
        assert len(results) == 0

    @clean_database
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
        results = get_paginated_expired_offer_ids(limit=2, page=0)

        # Then
        assert len(results) == 1
        assert offer1 in results
        assert offer2 not in results

    @clean_database
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
        results = get_paginated_expired_offer_ids(limit=2, page=0)

        # Then
        assert len(results) == 1
        assert offer1 in results
        assert offer2 not in results

    @clean_database
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
        results = get_paginated_expired_offer_ids(limit=2, page=0)

        # Then
        assert len(results) == 1
        assert offer1 in results
        assert offer2 not in results

    @clean_database
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
        results = get_paginated_expired_offer_ids(limit=2, page=0)

        # Then
        assert len(results) == 1
        assert offer1 in results
        assert offer2 not in results

    @clean_database
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
        results = get_paginated_expired_offer_ids(limit=2, page=0)

        # Then
        assert results == []
