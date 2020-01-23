import random
from datetime import datetime, timedelta

from freezegun import freeze_time

from models import Offer, Stock, Product
from models.offer_type import EventType, ThingType
from repository import repository
from repository.offer_queries import department_or_national_offers, \
    find_activation_offers, \
    find_offers_with_filter_parameters, \
    get_offers_for_recommendations_search, \
    get_active_offers, \
    get_offers_by_venue_id, _has_remaining_stock, order_by_with_criteria, get_paginated_active_offer_ids, \
    get_paginated_offer_ids_by_venue_id_and_last_provider_id, _order_by_occurs_soon_or_is_thing_then_randomize, \
    get_paginated_offer_ids_by_venue_id, get_offers_by_ids
from tests.conftest import clean_database
from tests.model_creators.generic_creators import create_booking, create_criterion, create_user, create_offerer, \
    create_venue, create_user_offerer, create_mediation, create_favorite, create_provider
from tests.model_creators.specific_creators import create_product_with_thing_type, create_offer_with_thing_product, \
    create_product_with_event_type, create_offer_with_event_product, create_event_occurrence, \
    create_stock_from_event_occurrence, create_stock_from_offer, create_stock_with_thing_offer, \
    create_stock_with_event_offer

REFERENCE_DATE = '2017-10-15 09:21:34'


class DepartmentOrNationalOffersTest:
    @clean_database
    def test_returns_national_thing_with_different_department(self, app):
        # given
        product = create_product_with_thing_type(thing_name='Lire un livre', is_national=True)
        offerer = create_offerer()
        venue = create_venue(offerer, postal_code='34000', departement_code='34')
        offer = create_offer_with_thing_product(venue, product)
        from repository import repository
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
        offer = create_offer_with_event_product(venue, product)
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
        offer = create_offer_with_event_product(venue, product)
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
        offer = create_offer_with_event_product(venue, product)
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
        offer = create_offer_with_event_product(venue, product)
        repository.save(offer)
        query = Product.query.filter_by(name='Voir une pièce')

        # when
        query = department_or_national_offers(query, ['29'])

        # then
        assert query.count() == 1


@freeze_time(REFERENCE_DATE)
class GetOffersForRecommendationsSearchTest:
    @clean_database
    def test_should_return_only_offers_on_events_of_that_type_when_searching_by_one_event_type(self, app):
        # Given
        type_label = EventType.CONFERENCE_DEBAT_DEDICACE
        other_type_label = EventType.MUSIQUE

        conference_event1 = create_product_with_event_type('Rencontre avec Franck Lepage', event_type=type_label)
        conference_event2 = create_product_with_event_type('Conférence ouverte', event_type=type_label)
        concert_event = create_product_with_event_type('Concert de Gael Faye', event_type=other_type_label)

        offerer = create_offerer(
            siren='507633576',
            address='1 BD POISSONNIERE',
            city='Paris',
            postal_code='75002',
            name='LE GRAND REX PARIS',
            validation_token=None,
        )
        venue = create_venue(
            offerer,
            name='LE GRAND REX PARIS',
            address="1 BD POISSONNIERE",
            postal_code='75002',
            city="Paris",
            departement_code='75',
            is_virtual=False,
            longitude="2.4002701",
            latitude="48.8363788",
            siret="50763357600016"
        )

        conference_offer1 = create_offer_with_event_product(venue, conference_event1)
        conference_offer2 = create_offer_with_event_product(venue, conference_event2)
        concert_offer = create_offer_with_event_product(venue, concert_event)

        conference_event_occurrence1 = create_event_occurrence(conference_offer1)
        conference_event_occurrence2 = create_event_occurrence(conference_offer2)
        concert_event_occurrence = create_event_occurrence(concert_offer)

        conference_stock1 = create_stock_from_event_occurrence(conference_event_occurrence1)
        conference_stock2 = create_stock_from_event_occurrence(conference_event_occurrence2)
        concert_stock = create_stock_from_event_occurrence(concert_event_occurrence)

        repository.save(conference_stock1, conference_stock2, concert_stock)

        # When
        offers = get_offers_for_recommendations_search(
            type_values=[
                str(type_label)
            ],
        )

        # Then
        assert conference_offer1 in offers
        assert conference_offer2 in offers
        assert concert_offer not in offers

    @clean_database
    def test_should_return_only_offers_on_things_of_that_type_when_searching_by_one_thing_type(self, app):
        # Given
        type_label_ok = ThingType.JEUX_VIDEO
        type_label_ko = ThingType.LIVRE_EDITION

        thing_ok1 = create_product_with_thing_type(thing_type=type_label_ok)
        thing_ok2 = create_product_with_thing_type(thing_type=type_label_ok)
        thing_ko = create_product_with_thing_type(thing_type=type_label_ko)
        event_ko = create_product_with_event_type(event_type=EventType.CINEMA)

        offerer = create_offerer()
        venue = create_venue(offerer)

        ok_offer_1 = create_offer_with_thing_product(venue, thing_ok1)
        ok_offer_2 = create_offer_with_thing_product(venue, thing_ok2)
        ko_offer = create_offer_with_thing_product(venue, thing_ko)
        ko_event_offer = create_offer_with_event_product(venue, event_ko)

        ko_event_occurrence = create_event_occurrence(ko_event_offer)

        ok_stock1 = create_stock_from_offer(ok_offer_1)
        ok_stock2 = create_stock_from_offer(ok_offer_2)
        ko_stock1 = create_stock_from_offer(ko_offer)
        ko_stock2 = create_stock_from_event_occurrence(ko_event_occurrence)

        repository.save(ok_stock1, ok_stock2, ko_stock1, ko_stock2)

        # When
        offers = get_offers_for_recommendations_search(
            type_values=[
                str(type_label_ok)
            ],
        )

        # Then
        assert len(offers) == 2
        assert ok_offer_1 in offers
        assert ok_offer_2 in offers

    @clean_database
    def test_should_return_recommendations_starting_during_time_interval_when_searching_by_datetime_only(self, app):
        # Duplicate
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer)

        ok_stock = _create_event_stock_and_offer_for_date(venue, datetime(2018, 1, 6, 12, 30))
        ko_stock_before = _create_event_stock_and_offer_for_date(venue, datetime(2018, 1, 1, 12, 30))
        ko_stock_after = _create_event_stock_and_offer_for_date(venue, datetime(2018, 1, 10, 12, 30))
        ok_stock_with_thing = create_stock_with_thing_offer(offerer, venue)

        repository.save(ok_stock, ko_stock_before, ko_stock_after)

        # When
        search_result_offers = get_offers_for_recommendations_search(
            days_intervals=[
                [datetime(2018, 1, 6, 12, 0), datetime(2018, 1, 6, 13, 0)]
            ],
        )

        # Then
        assert ok_stock.resolvedOffer in search_result_offers
        assert ok_stock_with_thing.resolvedOffer in search_result_offers
        assert ko_stock_before.resolvedOffer not in search_result_offers
        assert ko_stock_after.resolvedOffer not in search_result_offers

    @clean_database
    def test_should_return_things_and_events_with_name_containing_keywords_when_searching_with_several_partial_keywords(
            self, app):
        # Given
        thing_ok = create_product_with_thing_type(thing_name='Rencontre de michel')
        thing_product = create_product_with_thing_type(thing_name='Rencontre avec jean-luc')
        event_product = create_product_with_event_type(event_name='Rencontre avec jean-mimi chelou')
        offerer = create_offerer()
        venue = create_venue(offerer)
        thing_ok_offer = create_offer_with_thing_product(venue, thing_ok)
        thing_ko_offer = create_offer_with_thing_product(venue, thing_product)
        event_ko_offer = create_offer_with_event_product(venue, event_product)
        event_ko_occurrence = create_event_occurrence(event_ko_offer)
        event_ko_stock = create_stock_from_event_occurrence(event_ko_occurrence)
        thing_ok_stock = create_stock_from_offer(thing_ok_offer)
        thing_ko_stock = create_stock_from_offer(thing_ko_offer)
        repository.save(event_ko_stock, thing_ok_stock, thing_ko_stock)

        # When
        offers = get_offers_for_recommendations_search(keywords_string='renc michel')

        # Then
        assert thing_ok_offer in offers
        assert thing_ko_offer not in offers
        assert event_ko_offer not in offers

    @clean_database
    def test_should_matches_offer_with_accents_when_searching_without_accents_1(self, app):
        # Given
        thing_product_ok = create_product_with_thing_type(thing_name='Nez à nez')
        offerer = create_offerer()
        venue = create_venue(offerer)
        thing_ok_offer = create_offer_with_thing_product(venue, thing_product_ok)
        thing_ok_stock = create_stock_from_offer(thing_ok_offer)
        repository.save(thing_ok_stock)

        # When
        offers = get_offers_for_recommendations_search(keywords_string='nez a')

        # Then
        assert thing_ok_offer in offers

    @clean_database
    def test_should_matches_offer_with_accents_when_searching_without_accents_2(self, app):
        # Given
        thing_ok = create_product_with_thing_type(thing_name='Déjà')
        offerer = create_offerer()
        venue = create_venue(offerer)
        thing_ok_offer = create_offer_with_thing_product(venue, thing_ok)
        thing_ok_stock = create_stock_from_offer(thing_ok_offer)
        repository.save(thing_ok_stock)

        # When
        offers = get_offers_for_recommendations_search(keywords_string='deja')

        #
        assert thing_ok_offer in offers

    @clean_database
    def test_should_not_return_offers_by_types_with_booking_limit_date_over_when_searching(self, app):
        # Given
        three_hours_ago = datetime.utcnow() - timedelta(hours=3)
        type_label = ThingType.JEUX_VIDEO
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue, thing_type=type_label)
        outdated_stock = create_stock_from_offer(offer, booking_limit_datetime=three_hours_ago)

        repository.save(outdated_stock)

        # When
        search_result_offers = get_offers_for_recommendations_search(type_values=[
            str(type_label)
        ], )

        # Then
        assert not search_result_offers

    @clean_database
    def test_should_not_return_offers_by_types_with_all_beginning_datetime_passed_and_no_booking_limit_datetime_when_searching(
            self, app):
        # Given
        three_hours_ago = datetime.utcnow() - timedelta(hours=3)
        type_label = EventType.MUSEES_PATRIMOINE
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_event_product(venue, event_type=type_label)
        outdated_event_occurrence = create_event_occurrence(offer, beginning_datetime=three_hours_ago,
                                                            end_datetime=datetime.utcnow())
        stock = create_stock_from_event_occurrence(outdated_event_occurrence, booking_limit_date=None)

        repository.save(stock)

        # When
        search_result_offers = get_offers_for_recommendations_search(type_values=[
            str(type_label)
        ], )

        # Then
        assert not search_result_offers

    @clean_database
    def test_should_return_offers_by_types_with_some_but_not_all_beginning_datetime_passed_and_no_booking_limit_datetime_when_searching(
            self, app):
        # Given
        three_hours_ago = datetime.utcnow() - timedelta(hours=3)
        in_three_hours = datetime.utcnow() + timedelta(hours=3)
        in_four_hours = datetime.utcnow() + timedelta(hours=4)
        type_label = EventType.MUSEES_PATRIMOINE
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_event_product(venue, event_type=type_label)
        outdated_event_occurrence = create_event_occurrence(offer, beginning_datetime=three_hours_ago,
                                                            end_datetime=datetime.utcnow())
        future_event_occurrence = create_event_occurrence(offer, beginning_datetime=in_three_hours,
                                                          end_datetime=in_four_hours)
        future_stock = create_stock_from_event_occurrence(future_event_occurrence, booking_limit_date=None)
        outdated_stock = create_stock_from_event_occurrence(outdated_event_occurrence, booking_limit_date=None)

        repository.save(future_stock, outdated_stock)

        # When
        search_result_offers = get_offers_for_recommendations_search(type_values=[
            str(type_label)
        ], )

        # Then
        assert offer in search_result_offers

    @clean_database
    def test_should_not_return_duplicate_when_searching(self, app):
        # Given
        things_stock = []
        for x in range(0, 120):
            thing = create_product_with_thing_type(thing_name='snif')
            offerer = create_offerer(siren=str(random.randrange(123456789, 923456789)))
            venue = create_venue(offerer, siret=str(random.randrange(123123456789, 999923456789)))
            thing_offer = create_offer_with_thing_product(venue, thing)
            thing_stock = create_stock_from_offer(thing_offer)

            things_stock.append(thing_stock)

        repository.save(*things_stock)

        # When
        search_result_offers = get_offers_for_recommendations_search(page=1, keywords_string='snif')
        search_result_offers = search_result_offers + get_offers_for_recommendations_search(page=2,
                                                                                            keywords_string='snif')

        # Then
        assert len(search_result_offers) == len(set(search_result_offers))

    @clean_database
    def test_should_not_return_deactivated_offer_when_searching(self, app):
        # Given
        thing = create_product_with_thing_type()
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue, thing, is_active=False)
        thing_stock = create_stock_from_offer(offer)

        repository.save(thing_stock)

        # When
        search_result_offers = get_offers_for_recommendations_search(page=None)

        # Then
        assert offer not in search_result_offers

    @clean_database
    def test_should_not_return_offers_with_not_validated_offerer_when_searching(self, app):
        # Given
        thing = create_product_with_thing_type()
        offerer = create_offerer(validation_token='not_validated')
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue, thing)
        thing_stock = create_stock_from_offer(offer)

        repository.save(thing_stock)

        # When
        search_result_offers = get_offers_for_recommendations_search(page=None)

        # Then
        assert offer not in search_result_offers

    @clean_database
    def test_should_not_return_offers_with_deactivated_offerer_when_searching(self, app):
        # Given
        thing = create_product_with_thing_type()
        offerer = create_offerer(is_active=False)
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue, thing)
        thing_stock = create_stock_from_offer(offer)

        repository.save(thing_stock)

        # When
        search_result_offers = get_offers_for_recommendations_search(page=None)

        # Then
        assert offer not in search_result_offers

    @clean_database
    def test_should_not_return_offers_with_not_validated_venue_when_searching(self, app):
        # Given
        thing = create_product_with_thing_type()
        offerer = create_offerer()
        venue = create_venue(offerer, validation_token='not_validated')
        offer = create_offer_with_thing_product(venue, thing)
        thing_stock = create_stock_from_offer(offer)

        repository.save(thing_stock)

        # When
        search_result_offers = get_offers_for_recommendations_search(page=None)

        # Then
        assert offer not in search_result_offers

    @clean_database
    def test_should_not_return_offers_with_not_bookable_soft_deleted_stock_when_searching(self, app):
        # Given
        thing = create_product_with_thing_type()
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer_with_soft_deleted_stock = create_offer_with_thing_product(venue, thing)
        thing_stock = create_stock_from_offer(offer_with_soft_deleted_stock, soft_deleted=True)

        repository.save(thing_stock)

        # When
        search_result_offers = get_offers_for_recommendations_search(page=None)

        # Then
        assert offer_with_soft_deleted_stock not in search_result_offers

    @clean_database
    def test_should_not_return_offers_with_past_booking_limit_datetime_when_searching(self, app):
        # Given
        thing = create_product_with_thing_type()
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer_with_passed_booking_limit_datetime = create_offer_with_thing_product(venue, thing)
        thing_stock = create_stock_from_offer(offer_with_passed_booking_limit_datetime,
                                              booking_limit_datetime=datetime(2010, 1, 6, 12, 30))

        repository.save(thing_stock)

        # When
        search_result_offers = get_offers_for_recommendations_search(page=None)

        # Then
        assert offer_with_passed_booking_limit_datetime not in search_result_offers

    @clean_database
    def test_should_not_return_offer_in_past_when_searching(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer_in_past = _create_event_stock_and_offer_for_date(venue, datetime(2018, 1, 6, 12, 30))

        repository.save(offer_in_past)

        # When
        search_result_offers = get_offers_for_recommendations_search(page=None)

        # Then
        assert offer_in_past not in search_result_offers

    @clean_database
    def test_should_not_return_offers_with_not_available_stock_when_searching(self, app):
        # Given
        thing = create_product_with_thing_type()
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer_with_not_available_stock = create_offer_with_thing_product(venue, thing)
        thing_stock = create_stock_from_offer(offer_with_not_available_stock, available=0)

        repository.save(thing_stock)

        # When
        search_result_offers = get_offers_for_recommendations_search(page=None)

        # Then
        assert offer_with_not_available_stock not in search_result_offers

    @clean_database
    def test_should_not_return_offers_with_no_stock_when_searching(self, app):
        # Given
        thing = create_product_with_thing_type()
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer_with_no_stock = create_offer_with_thing_product(venue, thing)

        repository.save(offer_with_no_stock)

        # When
        search_result_offers = get_offers_for_recommendations_search(page=None)

        # Then
        assert offer_with_no_stock not in search_result_offers


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
        offer2 = create_offer_with_thing_product(venue1, thing_type=ThingType.AUDIOVISUEL)
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
        stock1 = create_stock_from_offer(offer1, price=0, available=0)
        stock2 = create_stock_from_offer(offer2, price=0, available=10)
        stock3 = create_stock_from_offer(offer3, price=0, available=1)
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
    def test_find_offers_with_filter_parameters_with_partial_keywords_and_filter_by_venue(self, app):
        user = create_user(email='offerer@email.com')
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
        ok_offer1 = create_offer_with_event_product(venue1, ok_product_event)
        ok_offer2 = create_offer_with_thing_product(venue1, ok_product_thing)
        ko_offer2 = create_offer_with_event_product(venue1, event_product2)
        ko_offer3 = create_offer_with_thing_product(ko_venue3, thing1_product)
        ko_offer4 = create_offer_with_thing_product(venue2, thing2_product)
        repository.save(
            user_offerer1, user_offerer2, ko_offerer3,
            ok_offer1, ko_offer2, ko_offer3, ko_offer4
        )

        # when
        offers = find_offers_with_filter_parameters(
            user,
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
        offer = create_offer_with_thing_product(venue, product)
        repository.save(offer)

        # When
        offers = get_offers_by_venue_id(venue.id)

        # Then
        assert len(offers) == 1
        assert offers[0].venueId == venue.id


class HasRemainingStockTest:
    @clean_database
    def test_should_return_0_offer_when_there_is_no_stock(self, app):
        # Given
        thing = create_product_with_thing_type()
        user = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue, thing)
        repository.save(offer)

        # When
        offers_count = Offer.query \
            .join(Stock) \
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
        offer = create_offer_with_thing_product(venue, thing)
        stock = create_stock_from_offer(offer, available=4, price=0)
        booking_1 = create_booking(user=user, stock=stock, quantity=2)
        booking_2 = create_booking(user=user, stock=stock, quantity=1)
        repository.save(stock, booking_1, booking_2)

        # When
        offers_count = Offer.query \
            .join(Stock) \
            .filter(_has_remaining_stock()) \
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
        offer = create_offer_with_thing_product(venue, thing)
        stock = create_stock_from_offer(offer, available=3, price=0)
        booking_1 = create_booking(user=user, stock=stock, quantity=2)
        booking_2 = create_booking(user=user, stock=stock, quantity=1)
        repository.save(stock, booking_1, booking_2)

        # When
        offers_count = Offer.query \
            .join(Stock) \
            .filter(_has_remaining_stock()) \
            .count()

        # Then
        assert offers_count == 0

    @clean_database
    def test_should_return_1_offer_when_stock_was_updated_after_booking_was_used(self, app):
        # Given
        thing = create_product_with_thing_type()
        user = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue, thing)
        stock = create_stock_from_offer(offer, available=1, price=0)
        booking = create_booking(user=user, stock=stock, is_used=True, quantity=1)
        stock.dateModified = datetime.utcnow() + timedelta(days=1)
        repository.save(stock, booking)

        # When
        offers_count = Offer.query \
            .join(Stock) \
            .filter(_has_remaining_stock()) \
            .count()

        # Then
        assert offers_count == 1

    @clean_database
    def test_should_return_1_offer_when_booking_was_cancelled(app):
        # Given
        user = create_user()
        product = create_product_with_thing_type(thing_name='Lire un livre', is_national=True)
        offerer = create_offerer()
        venue = create_venue(offerer, postal_code='34000', departement_code='34')
        offer = create_offer_with_thing_product(venue, product)
        stock = create_stock_from_offer(offer, available=2)
        booking = create_booking(user=user, stock=stock, is_cancelled=True, quantity=2, venue=venue)
        repository.save(booking)

        # When
        offers_count = Offer.query \
            .join(Stock) \
            .filter(_has_remaining_stock()) \
            .count()

        # Then
        assert offers_count == 1

    @clean_database
    def test_should_return_0_offer_when_there_is_no_remaining_stock(app):
        # Given
        product = create_product_with_thing_type(thing_name='Lire un livre', is_national=True)
        offerer = create_offerer()
        venue = create_venue(offerer, postal_code='34000', departement_code='34')
        offer = create_offer_with_thing_product(venue, product)
        stock = create_stock_from_offer(offer, available=2, price=0)
        user = create_user()
        booking1 = create_booking(user=user, stock=stock, is_cancelled=True, quantity=2, venue=venue)
        booking2 = create_booking(user=user, stock=stock, quantity=2, venue=venue)
        repository.save(booking1, booking2)

        # When
        offers_count = Offer.query \
            .join(Stock) \
            .filter(_has_remaining_stock()) \
            .count()

        # Then
        assert offers_count == 0

    @clean_database
    def test_should_return_1_offer_when_there_are_one_full_stock_and_one_empty_stock(app):
        # Given
        product = create_product_with_thing_type(thing_name='Lire un livre', is_national=True)
        offerer = create_offerer()
        venue = create_venue(offerer, postal_code='34000', departement_code='34')
        offer = create_offer_with_thing_product(venue, product)
        stock1 = create_stock_from_offer(offer, available=2, price=0)
        stock2 = create_stock_from_offer(offer, available=2, price=0)
        user = create_user()
        booking1 = create_booking(user=user, stock=stock1, quantity=2, venue=venue)
        repository.save(booking1, stock2)

        # When
        offers_count = Offer.query \
            .join(Stock) \
            .filter(_has_remaining_stock()) \
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

        offer1 = create_offer_with_thing_product(venue)
        offer2 = create_offer_with_thing_product(venue)

        offer1.criteria = [criterion_negative]
        offer2.criteria = [criterion_negative, criterion_positive]

        repository.save(offer1, offer2)

        # When
        offers = Offer.query \
            .order_by(Offer.baseScore.desc()) \
            .all()

        # Then
        assert offers == [offer2, offer1]


class GetActiveOffersTest:
    @clean_database
    def test_when_department_code_00(self, app):
        # Given
        offerer = create_offerer(siren='123456789')
        user = create_user()
        venue_34 = create_venue(offerer, postal_code='34000', departement_code='34', siret=offerer.siren + '11111')
        venue_93 = create_venue(offerer, postal_code='93000', departement_code='93', siret=offerer.siren + '22222')
        venue_75 = create_venue(offerer, postal_code='75000', departement_code='75', siret=offerer.siren + '33333')
        offer_34 = create_offer_with_thing_product(venue_34)
        offer_93 = create_offer_with_thing_product(venue_93)
        offer_75 = create_offer_with_thing_product(venue_75)
        stock_34 = create_stock_from_offer(offer_34)
        stock_93 = create_stock_from_offer(offer_93)
        stock_75 = create_stock_from_offer(offer_75)
        create_mediation(stock_34.offer)
        create_mediation(stock_93.offer)
        create_mediation(stock_75.offer)

        repository.save(stock_34, stock_93, stock_75)

        # When
        offers = get_active_offers(departement_codes=['00'],
                                   offer_id=None,
                                   pagination_params={'seed': 0.9, 'page': 1},
                                   user=user)

        # Then
        assert offer_34 in offers
        assert offer_93 in offers
        assert offer_75 in offers

    @clean_database
    def test_should_not_return_activation_event(self, app):
        # Given
        offerer = create_offerer(siren='123456789')
        user = create_user()
        venue_93 = create_venue(offerer, postal_code='93000', departement_code='93', siret=offerer.siren + '33333')
        offer_93 = create_offer_with_event_product(venue_93, thumb_count=1)
        offer_activation_93 = create_offer_with_event_product(venue_93, event_type=EventType.ACTIVATION,
                                                              thumb_count=1)
        stock_93 = create_stock_from_offer(offer_93)
        stock_activation_93 = create_stock_from_offer(offer_activation_93)
        create_mediation(stock_93.offer)
        create_mediation(stock_activation_93.offer)

        repository.save(stock_93, stock_activation_93)

        # When
        offers = get_active_offers(departement_codes=['00'],
                                   offer_id=None,
                                   pagination_params={'seed': 0.9, 'page': 1},
                                   user=user)

        # Then
        assert offer_93 in offers
        assert offer_activation_93 not in offers

    @clean_database
    def test_should_not_return_activation_thing(self, app):
        # Given
        offerer = create_offerer(siren='123456789')
        user = create_user()
        venue_93 = create_venue(offerer, postal_code='93000', departement_code='93', siret=offerer.siren + '33333')
        offer_93 = create_offer_with_thing_product(venue_93, thumb_count=1)
        offer_activation_93 = create_offer_with_thing_product(venue_93, thing_type=ThingType.ACTIVATION,
                                                              thumb_count=1)
        stock_93 = create_stock_from_offer(offer_93)
        stock_activation_93 = create_stock_from_offer(offer_activation_93)
        create_mediation(stock_93.offer)
        create_mediation(stock_activation_93.offer)

        repository.save(stock_93, stock_activation_93)

        # When
        offers = get_active_offers(departement_codes=['00'],
                                   offer_id=None,
                                   pagination_params={'seed': 0.9, 'page': 1},
                                   user=user)

        # Then
        assert offer_93 in offers
        assert offer_activation_93 not in offers

    @clean_database
    def test_should_return_offers_with_stock(self, app):
        # Given
        product = create_product_with_thing_type(thing_name='Lire un livre', is_national=True)
        offerer = create_offerer()
        user = create_user()
        venue = create_venue(offerer, postal_code='34000', departement_code='34')
        offer = create_offer_with_thing_product(venue, product)
        stock = create_stock_from_offer(offer, available=2)
        create_mediation(stock.offer)
        repository.save(stock)

        # When
        offers = get_active_offers(departement_codes=['00'],
                                   offer_id=None,
                                   pagination_params={'seed': 0.9, 'page': 1},
                                   user=user)

        # Then
        assert len(offers) == 1

    @clean_database
    def test_should_return_offers_with_mediation_only(app):
        # Given
        offerer = create_offerer()
        user = create_user()
        venue = create_venue(offerer, postal_code='34000', departement_code='34')
        stock1 = create_stock_with_thing_offer(offerer, venue, name='thing_with_mediation')
        stock2 = create_stock_with_thing_offer(offerer, venue, name='thing_without_mediation')
        create_mediation(stock1.offer)
        repository.save(stock1, stock2)

        # When
        offers = get_active_offers(departement_codes=['00'],
                                   offer_id=None,
                                   pagination_params={'seed': 0.9, 'page': 1},
                                   user=user)

        # Then
        assert len(offers) == 1
        assert offers[0].name == 'thing_with_mediation'

    @clean_database
    def test_should_return_offers_that_occur_in_less_than_10_days_and_things_first(self, app):
        # Given
        offerer = create_offerer()
        user = create_user()
        venue = create_venue(offerer, postal_code='34000', departement_code='34')

        stock1 = create_stock_with_thing_offer(offerer, venue, name='thing')
        stock2 = create_stock_with_event_offer(offerer,
                                               venue,
                                               beginning_datetime=datetime.utcnow() + timedelta(days=4),
                                               end_datetime=datetime.utcnow() + timedelta(days=4, hours=2),
                                               name='event_occurs_soon',
                                               thumb_count=1)
        stock3 = create_stock_with_event_offer(offerer,
                                               venue,
                                               beginning_datetime=datetime.utcnow() + timedelta(days=11),
                                               end_datetime=datetime.utcnow() + timedelta(days=11, hours=2),
                                               name='event_occurs_later',
                                               thumb_count=1)
        create_mediation(stock1.offer)
        create_mediation(stock2.offer)
        create_mediation(stock3.offer)
        repository.save(stock1, stock2, stock3)

        # When
        offers = get_active_offers(departement_codes=['00'],
                                   offer_id=None,
                                   pagination_params={'seed': 0.9, 'page': 1},
                                   user=user)

        # Then
        assert len(offers) == 3
        assert (offers[0].name == 'event_occurs_soon'
                and offers[1].name == 'thing') \
               or (offers[1].name == 'event_occurs_soon'
                   and offers[0].name == 'thing')
        assert offers[2].name == 'event_occurs_later'

    @clean_database
    def test_should_return_offers_with_varying_types(self, app):
        # Given
        offerer = create_offerer()
        user = create_user()
        venue = create_venue(offerer, postal_code='34000', departement_code='34')
        stock1 = create_stock_with_thing_offer(offerer, venue, name='thing', thing_type=ThingType.JEUX_VIDEO)
        stock2 = create_stock_with_thing_offer(offerer, venue, name='thing', thing_type=ThingType.CINEMA_ABO,
                                               url='http://example.com')
        stock3 = create_stock_with_thing_offer(offerer, venue, name='thing', thing_type=ThingType.JEUX_VIDEO)
        stock4 = create_stock_with_thing_offer(offerer, venue, name='thing', thing_type=ThingType.JEUX_VIDEO)
        stock5 = create_stock_with_thing_offer(offerer, venue, name='thing', thing_type=ThingType.AUDIOVISUEL)
        stock6 = create_stock_with_thing_offer(offerer, venue, name='thing', thing_type=ThingType.JEUX)
        create_mediation(stock1.offer)
        create_mediation(stock2.offer)
        create_mediation(stock3.offer)
        create_mediation(stock4.offer)
        create_mediation(stock5.offer)
        create_mediation(stock6.offer)
        repository.save(stock1, stock2, stock3, stock4, stock5, stock6)

        def _first_four_offers_have_different_type_and_onlineness(offers):
            return len(set([o.type + (o.url or '')
                            for o in offers[:4]])) == 4

        # When
        offers = get_active_offers(departement_codes=['00'],
                                   offer_id=None,
                                   pagination_params={'seed': 0.9, 'page': 1},
                                   user=user)

        # Then
        assert len(offers) == 6
        assert _first_four_offers_have_different_type_and_onlineness(offers)

    @clean_database
    def test_should_not_return_offers_with_no_stock(self, app):
        # Given
        product = create_product_with_thing_type(thing_name='Lire un livre', is_national=True)
        offerer = create_offerer()
        user = create_user()
        venue = create_venue(offerer, postal_code='34000', departement_code='34')
        offer = create_offer_with_thing_product(venue, product)
        stock = create_stock_from_offer(offer, available=2, price=0)
        booking1 = create_booking(user=user, stock=stock, is_cancelled=True, quantity=2, venue=venue)
        booking2 = create_booking(user=user, stock=stock, quantity=2, venue=venue)
        create_mediation(stock.offer)
        repository.save(booking1, booking2)

        # When
        offers = get_active_offers(departement_codes=['00'],
                                   offer_id=None,
                                   pagination_params={'seed': 0.9, 'page': 1},
                                   user=user)

        # Then
        assert len(offers) == 0

    @clean_database
    def test_should_return_same_number_of_recommendation(self, app):
        # Given
        offerer = create_offerer()
        user = create_user()
        venue = create_venue(offerer, postal_code='34000', departement_code='34')

        stock1 = create_stock_with_thing_offer(offerer, venue, name='thing', thing_type=ThingType.JEUX_VIDEO)
        stock2 = create_stock_with_thing_offer(offerer, venue, name='thing', thing_type=ThingType.JEUX_VIDEO)
        stock3 = create_stock_with_thing_offer(offerer, venue, name='thing', thing_type=ThingType.AUDIOVISUEL)
        stock4 = create_stock_with_thing_offer(offerer, venue, name='thing', thing_type=ThingType.JEUX)
        create_mediation(stock1.offer)
        create_mediation(stock2.offer)
        create_mediation(stock3.offer)
        create_mediation(stock4.offer)

        repository.save(stock1, stock2, stock3, stock4)

        # When
        offers = get_active_offers(departement_codes=['00'],
                                   offer_id=None,
                                   pagination_params={'seed': 0.9, 'page': 1},
                                   user=user)

        # Then
        assert len(offers) == 4

    @clean_database
    def test_with_criteria_should_return_offer_with_highest_base_score_first(self, app):
        # Given
        offerer = create_offerer()
        user = create_user()
        venue = create_venue(offerer, postal_code='34000', departement_code='34')

        offer1 = create_offer_with_thing_product(venue, thing_type=ThingType.JEUX_VIDEO, thumb_count=1)
        stock1 = create_stock_from_offer(offer1, price=0)
        offer1.criteria = [create_criterion(name='negative', score_delta=-1)]

        offer2 = create_offer_with_thing_product(venue, thing_type=ThingType.JEUX_VIDEO, thumb_count=1)
        stock2 = create_stock_from_offer(offer2, price=0)
        offer2.criteria = [create_criterion(name='positive', score_delta=1)]

        create_mediation(stock1.offer)
        create_mediation(stock2.offer)

        repository.save(stock1, stock2)

        # When
        offers = get_active_offers(departement_codes=['00'],
                                   offer_id=None,
                                   order_by=order_by_with_criteria,
                                   pagination_params={'seed': 0.9, 'page': 1},
                                   user=user)

        # Then
        assert offers == [offer2, offer1]

    @clean_database
    def test_with_criteria_should_return_offer_with_highest_base_score_first_bust_keep_the_partition(self, app):
        # Given
        offerer = create_offerer()
        user = create_user()
        venue = create_venue(offerer, postal_code='34000', departement_code='34')

        offer1 = create_offer_with_thing_product(venue, thing_type=ThingType.CINEMA_ABO, thumb_count=1)
        stock1 = create_stock_from_offer(offer1, price=0)
        offer1.criteria = [create_criterion(name='negative', score_delta=1)]

        offer2 = create_offer_with_thing_product(venue, thing_type=ThingType.CINEMA_ABO, thumb_count=1)
        stock2 = create_stock_from_offer(offer2, price=0)
        offer2.criteria = [create_criterion(name='positive', score_delta=2)]

        offer3 = create_offer_with_thing_product(venue, thing_type=ThingType.JEUX_VIDEO, thumb_count=1)
        stock3 = create_stock_from_offer(offer3, price=0)
        offer3.criteria = []

        create_mediation(stock1.offer)
        create_mediation(stock2.offer)
        create_mediation(stock3.offer)

        repository.save(stock1, stock2, stock3)

        # When
        offers = get_active_offers(departement_codes=['00'],
                                   offer_id=None,
                                   order_by=order_by_with_criteria,
                                   pagination_params={'seed': 0.9, 'page': 1},
                                   user=user)

        # Then
        assert offers == [offer2, offer3, offer1]

    @clean_database
    def test_should_return_offers_in_the_same_order_given_the_same_seed(self, app):
        # Given
        offerer = create_offerer()
        user = create_user()
        venue = create_venue(offerer, postal_code='34000', departement_code='34')

        offer1 = create_offer_with_thing_product(venue, thing_type=ThingType.CINEMA_ABO)
        stock1 = create_stock_from_offer(offer1, price=0)

        offer2 = create_offer_with_thing_product(venue, thing_type=ThingType.CINEMA_ABO)
        stock2 = create_stock_from_offer(offer2, price=0)

        offer3 = create_offer_with_thing_product(venue, thing_type=ThingType.CINEMA_ABO)
        stock3 = create_stock_from_offer(offer3, price=0)

        offer4 = create_offer_with_thing_product(venue, thing_type=ThingType.CINEMA_ABO)
        stock4 = create_stock_from_offer(offer4, price=0)

        create_mediation(stock1.offer)
        create_mediation(stock2.offer)
        create_mediation(stock3.offer)
        create_mediation(stock4.offer)

        repository.save(stock1, stock2, stock3, stock4)

        pagination_params = {'seed': 0.5, 'page': 1}
        offers_1 = get_active_offers(departement_codes=['00'],
                                     offer_id=None,
                                     order_by=_order_by_occurs_soon_or_is_thing_then_randomize,
                                     pagination_params=pagination_params,
                                     user=user)

        offers_2 = get_active_offers(departement_codes=['00'],
                                     offer_id=None,
                                     order_by=_order_by_occurs_soon_or_is_thing_then_randomize,
                                     pagination_params=pagination_params,
                                     user=user)

        offers_3 = get_active_offers(departement_codes=['00'],
                                     offer_id=None,
                                     order_by=_order_by_occurs_soon_or_is_thing_then_randomize,
                                     pagination_params=pagination_params,
                                     user=user)

        # When
        offers_4 = get_active_offers(departement_codes=['00'],
                                     offer_id=None,
                                     order_by=_order_by_occurs_soon_or_is_thing_then_randomize,
                                     pagination_params=pagination_params,
                                     user=user)

        # Then
        assert offers_1 == offers_4
        assert offers_2 == offers_4
        assert offers_3 == offers_4

    @clean_database
    def test_should_return_offers_not_in_the_same_order_given_different_seeds(self, app):
        # Given
        offerer = create_offerer()
        user = create_user()
        venue = create_venue(offerer, postal_code='34000', departement_code='34')

        offer1 = create_offer_with_thing_product(venue, thing_type=ThingType.CINEMA_ABO)
        stock1 = create_stock_from_offer(offer1, price=0)

        offer2 = create_offer_with_thing_product(venue, thing_type=ThingType.CINEMA_ABO)
        stock2 = create_stock_from_offer(offer2, price=0)

        offer3 = create_offer_with_thing_product(venue, thing_type=ThingType.CINEMA_ABO)
        stock3 = create_stock_from_offer(offer3, price=0)

        offer4 = create_offer_with_thing_product(venue, thing_type=ThingType.CINEMA_ABO)
        stock4 = create_stock_from_offer(offer4, price=0)

        create_mediation(stock1.offer)
        create_mediation(stock2.offer)
        create_mediation(stock3.offer)
        create_mediation(stock4.offer)

        repository.save(stock1, stock2, stock3, stock4)

        offers_1 = get_active_offers(departement_codes=['00'],
                                     offer_id=None,
                                     order_by=_order_by_occurs_soon_or_is_thing_then_randomize,
                                     pagination_params={'seed': 0.9, 'page': 1},
                                     user=user)

        # When
        offers_2 = get_active_offers(departement_codes=['00'],
                                     offer_id=None,
                                     order_by=_order_by_occurs_soon_or_is_thing_then_randomize,
                                     pagination_params={'seed': -0.8, 'page': 1},
                                     user=user)

        # Then
        assert offers_1 != offers_2

    @clean_database
    def test_should_not_return_booked_offers(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer, postal_code='34000', departement_code='34')
        offer = create_offer_with_thing_product(venue, thing_type=ThingType.CINEMA_ABO)
        stock = create_stock_from_offer(offer, price=0)
        user = create_user()
        booking = create_booking(user=user, stock=stock)
        create_mediation(stock.offer)
        repository.save(booking)

        # When
        offers = get_active_offers(departement_codes=['00'],
                                   offer_id=None,
                                   order_by=_order_by_occurs_soon_or_is_thing_then_randomize,
                                   pagination_params={'seed': 0.9, 'page': 1},
                                   user=user)

        # Then
        assert offers == []

    @clean_database
    def test_should_not_return_favorite_offers(self, app):
        # Given
        offerer = create_offerer()
        user = create_user()
        venue = create_venue(offerer, postal_code='34000', departement_code='34')

        offer = create_offer_with_thing_product(venue, thing_type=ThingType.CINEMA_ABO)
        stock = create_stock_from_offer(offer, price=0)
        mediation = create_mediation(stock.offer)
        favorite = create_favorite(mediation=mediation, offer=offer, user=user)

        repository.save(favorite)

        # When
        offers = get_active_offers(departement_codes=['00'],
                                   pagination_params={'seed': 0.9, 'page': 1},
                                   offer_id=None,
                                   order_by=_order_by_occurs_soon_or_is_thing_then_randomize,
                                   user=user)

        # Then
        assert offers == []

    @clean_database
    def test_should_return_different_offers_when_different_page_and_same_seed(self, app):
        # Given
        offerer = create_offerer()
        user = create_user()
        venue = create_venue(offerer)
        offer1 = create_offer_with_thing_product(idx=1, venue=venue)
        offer2 = create_offer_with_thing_product(idx=2, venue=venue)
        offer3 = create_offer_with_thing_product(idx=3, venue=venue)
        offer4 = create_offer_with_thing_product(idx=4, venue=venue)
        stock1 = create_stock_from_offer(offer1)
        stock2 = create_stock_from_offer(offer2)
        stock3 = create_stock_from_offer(offer3)
        stock4 = create_stock_from_offer(offer4)
        create_mediation(offer1)
        create_mediation(offer2)
        create_mediation(offer3)
        create_mediation(offer4)
        repository.save(stock1, stock2, stock3, stock4)

        # When
        offers1 = get_active_offers(departement_codes=['00'],
                                    limit=2,
                                    pagination_params={'page': 1, 'seed': 1},
                                    user=user)
        offers2 = get_active_offers(departement_codes=['00'],
                                    limit=2,
                                    pagination_params={'page': 2, 'seed': 1},
                                    user=user)
        offers3 = get_active_offers(departement_codes=['00'],
                                    limit=2,
                                    pagination_params={'page': 3, 'seed': 1},
                                    user=user)

        # Then
        assert len(offers1) == 2
        assert offers1 != offers2
        assert len(offers2) == 2
        assert len(offers3) == 0


def _create_event_stock_and_offer_for_date(venue, date):
    product = create_product_with_event_type()
    offer = create_offer_with_event_product(venue, product)
    event_occurrence = create_event_occurrence(offer, beginning_datetime=date, end_datetime=date + timedelta(hours=1))
    stock = create_stock_from_event_occurrence(event_occurrence, booking_limit_date=date)
    return stock


class GetOffersByIdsTest:
    @clean_database
    def test_should_return_all_existing_offers_when_offer_ids_are_given(self, app):
        # given
        offerer = create_offerer()
        venue = create_venue(offerer=offerer)
        offer1 = create_offer_with_thing_product(venue=venue, idx=1)
        offer2 = create_offer_with_thing_product(venue=venue, idx=2)
        repository.save(offer1, offer2)
        offer_ids = [0, 1, 2]

        # when
        offers = get_offers_by_ids(offer_ids)

        # then
        assert len(offers) == 2
        assert offers[0].id == 1
        assert offers[1].id == 2


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
        print(offer_ids)

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
        PcObject.save(offer1, offer2)

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


class GetPaginatedOfferIdsByVenueIdAndLastProviderId:
    @clean_database
    def test_should_return_offer_ids_when_exist_and_venue_id_and_last_provider_id_match(self, app):
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
        offer1 = create_offer_with_thing_product(last_provider_id=provider1.id, venue=venue)
        offer2 = create_offer_with_thing_product(last_provider_id=provider1.id, venue=venue)
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
        offer1 = create_offer_with_thing_product(last_provider_id=provider1.id, venue=venue)
        offer2 = create_offer_with_thing_product(last_provider_id=provider1.id, venue=venue)
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
