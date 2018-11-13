""" repository offer queries """
from datetime import datetime, timedelta

import pytest

from models import Thing, PcObject, Event
from models.offer_type import EventType, ThingType
from repository.offer_queries import departement_or_national_offers, \
    get_offers_for_recommendations_search, get_active_offers_by_type, find_activation_offers
from tests.conftest import clean_database
from utils.test_utils import create_event, \
    create_event_occurrence, \
    create_event_offer, \
    create_stock_from_event_occurrence, \
    create_thing, \
    create_thing_offer, \
    create_offerer, \
    create_venue, create_user, create_stock_from_offer, create_mediation, create_stock_with_thing_offer, create_booking


@pytest.mark.standalone
@clean_database
def test_departement_or_national_offers_with_national_thing_returns_national_thing(app):
    # Given
    thing = create_thing(thing_name='Lire un livre', is_national=True)
    offerer = create_offerer()
    venue = create_venue(offerer, departement_code='34')
    offer = create_thing_offer(venue, thing)
    PcObject.check_and_save(offer)
    query = Thing.query.filter_by(name='Lire un livre')
    # When
    query = departement_or_national_offers(query, Thing, ['93'])

    assert thing in query.all()


@pytest.mark.standalone
@clean_database
def test_departement_or_national_offers_with_national_event_returns_national_event(app):
    # Given
    event = create_event('Voir une pièce')
    offerer = create_offerer()
    venue = create_venue(offerer)
    offer = create_event_offer(venue, event)
    PcObject.check_and_save(offer)
    query = Event.query.filter_by(name='Voir une pièce')
    # When
    query = departement_or_national_offers(query, Event, ['93'])

    assert event in query.all()


@pytest.mark.standalone
@clean_database
def test_get_offers_for_recommendations_search_by_type(app):
    # Given
    type_label = str(EventType['CONFERENCE_DEBAT_DEDICACE'])
    other_type_label = str(EventType['MUSIQUE'])

    conference_event = create_event(
        'Rencontre avec Franck Lepage',
        type=type_label
    )
    concert_event = create_event(
        'Concert de Gael Faye',
        type=other_type_label
    )

    offerer = create_offerer(
        siren='507633576',
        address='1 BD POISSONNIERE',
        city='Paris',
        postal_code='75002',
        name='LE GRAND REX PARIS',
        validation_token=None,
        iban=None,
        bic=None
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

    conference_offer = create_event_offer(venue, conference_event)
    concert_offer = create_event_offer(venue, concert_event)

    conference_event_occurrence = create_event_occurrence(
        conference_offer
    )
    concert_event_occurrence = create_event_occurrence(
        concert_offer
    )

    conference_stock = create_stock_from_event_occurrence(conference_event_occurrence)
    concert_stock = create_stock_from_event_occurrence(concert_event_occurrence)

    PcObject.check_and_save(conference_stock, concert_stock)

    # When
    offers = get_offers_for_recommendations_search(
        type_values=[
            type_label
        ],
    )

    # Then
    assert conference_offer in offers
    assert concert_offer not in offers

def create_event_stock_and_offer_for_date(venue, date) :
    event = create_event()
    offer = create_event_offer(venue, event)
    event_occurrence = create_event_occurrence(offer, beginning_datetime=date, end_datetime=date+timedelta(hours=1))
    stock = create_stock_from_event_occurrence(event_occurrence)
    return stock

@pytest.mark.standalone
@clean_database
def test_get_offers_for_recommendations_search_by_datetime(app):
    # Given
    offerer = create_offerer()
    venue = create_venue(offerer)

    ok_stock = create_event_stock_and_offer_for_date(venue, datetime(2018, 1, 6, 12, 30))
    ko_stock_before = create_event_stock_and_offer_for_date(venue, datetime(2018, 1, 1, 12, 30))
    ko_stock_after = create_event_stock_and_offer_for_date(venue, datetime(2018, 1, 10, 12, 30))
    ok_stock_thing = create_stock_with_thing_offer(offerer, venue, None)

    PcObject.check_and_save(ok_stock, ko_stock_before, ko_stock_after)

    # When
    search_result_offers = get_offers_for_recommendations_search(
        days_intervals=[
            [ datetime(2018, 1, 6, 12, 0), datetime(2018, 1, 6, 13, 0) ]
        ],
    )

    # Then
    assert ok_stock.resolvedOffer in search_result_offers
    assert ok_stock_thing.resolvedOffer in search_result_offers
    assert ko_stock_before.resolvedOffer not in search_result_offers
    assert ko_stock_after.resolvedOffer not in search_result_offers


@clean_database
@pytest.mark.standalone
def test_get_active_offers_by_type_when_departement_code_00(app):
    # Given
    offerer = create_offerer()
    venue_34 = create_venue(offerer, postal_code='34000', departement_code='34', siret=offerer.siren + '11111')
    venue_93 = create_venue(offerer, postal_code='93000', departement_code='93', siret=offerer.siren + '22222')
    venue_75 = create_venue(offerer, postal_code='75000', departement_code='75', siret=offerer.siren + '33333')
    offer_34 = create_thing_offer(venue_34)
    offer_93 = create_thing_offer(venue_93)
    offer_75 = create_thing_offer(venue_75)
    stock_34 = create_stock_from_offer(offer_34)
    stock_93 = create_stock_from_offer(offer_93)
    stock_75 = create_stock_from_offer(offer_75)

    PcObject.check_and_save(stock_34, stock_93, stock_75)

    # When
    user = create_user(departement_code='00')
    offers = get_active_offers_by_type(Thing, user=user, departement_codes=['00'], offer_id=None)

    # Then
    assert offer_34 in offers
    assert offer_93 in offers
    assert offer_75 in offers


@clean_database
@pytest.mark.standalone
def test_get_active_event_offers_only_returns_event_offers(app):
    # Given
    user = create_user(departement_code='93')
    offerer = create_offerer()
    venue = create_venue(offerer, departement_code='93')
    offer1 = create_thing_offer(venue, thumb_count=1)
    offer2 = create_event_offer(venue, thumb_count=1)
    now = datetime.utcnow()
    event_occurrence = create_event_occurrence(offer2, beginning_datetime=now + timedelta(hours=72),
                                               end_datetime=now + timedelta(hours=74))
    mediation = create_mediation(offer2)
    stock1 = create_stock_from_offer(offer1, price=0)
    stock2 = create_stock_from_event_occurrence(event_occurrence, price=0, available=10,
                                                booking_limit_date=now + timedelta(days=2))
    PcObject.check_and_save(user, stock1, stock2, mediation, event_occurrence)

    # When
    offers = get_active_offers_by_type(Event, user=user, departement_codes=['93'])
    # Then
    assert len(offers) == 1
    assert offers[0].id == offer2.id


@clean_database
@pytest.mark.standalone
def test_find_activation_offers_returns_activation_offers_in_given_departement(app):
    # given
    offerer = create_offerer()
    venue1 = create_venue(offerer, siret=offerer.siren + '12345', postal_code='34000', departement_code='34')
    venue2 = create_venue(offerer, siret=offerer.siren + '54321', postal_code='93000', departement_code='93')
    offer1 = create_event_offer(venue1, event_type=EventType.ACTIVATION)
    offer2 = create_event_offer(venue1, event_type=EventType.SPECTACLE_VIVANT)
    offer3 = create_event_offer(venue2, event_type=EventType.ACTIVATION)
    stock1 = create_stock_from_offer(offer1)
    stock2 = create_stock_from_offer(offer2)
    stock3 = create_stock_from_offer(offer3)
    PcObject.check_and_save(stock1, stock2, stock3)

    # when
    offers = find_activation_offers('34').all()

    # then
    assert len(offers) == 1


@clean_database
@pytest.mark.standalone
def test_find_activation_offers_returns_activation_offers_if_offer_is_national(app):
    # given
    offerer = create_offerer()
    venue1 = create_venue(offerer, siret=offerer.siren + '12345', postal_code='34000', departement_code='34')
    venue2 = create_venue(offerer, siret=offerer.siren + '54321', postal_code='93000', departement_code='93')
    offer1 = create_event_offer(venue1, event_type=EventType.ACTIVATION)
    offer2 = create_thing_offer(venue1, thing_type=ThingType.AUDIOVISUEL)
    offer3 = create_event_offer(venue2, event_type=EventType.ACTIVATION, is_national=True)
    offer4 = create_event_offer(venue2, event_type=EventType.ACTIVATION, is_national=True)
    stock1 = create_stock_from_offer(offer1)
    stock2 = create_stock_from_offer(offer2)
    stock3 = create_stock_from_offer(offer3)
    stock4 = create_stock_from_offer(offer4)
    PcObject.check_and_save(stock1, stock2, stock3, stock4)

    # when
    offers = find_activation_offers('34').all()

    # then
    assert len(offers) == 3


@clean_database
@pytest.mark.standalone
def test_find_activation_offers_returns_activation_offers_in_all_ile_de_france_if_departement_is_93(app):
    # given
    offerer = create_offerer()
    venue1 = create_venue(offerer, siret=offerer.siren + '12345', postal_code='34000', departement_code='34')
    venue2 = create_venue(offerer, siret=offerer.siren + '67890', postal_code='75000', departement_code='75')
    venue3 = create_venue(offerer, siret=offerer.siren + '54321', postal_code='78000', departement_code='78')
    offer1 = create_event_offer(venue1, event_type=EventType.ACTIVATION)
    offer2 = create_event_offer(venue2, event_type=EventType.ACTIVATION)
    offer3 = create_event_offer(venue3, event_type=EventType.ACTIVATION)
    stock1 = create_stock_from_offer(offer1)
    stock2 = create_stock_from_offer(offer2)
    stock3 = create_stock_from_offer(offer3)
    PcObject.check_and_save(stock1, stock2, stock3)

    # when
    offers = find_activation_offers('93').all()

    # then
    assert len(offers) == 2


@clean_database
@pytest.mark.standalone
def test_find_activation_offers_returns_activation_offers_with_available_stocks(app):
    # given
    offerer = create_offerer()
    venue1 = create_venue(offerer, siret=offerer.siren + '12345', postal_code='93000', departement_code='93')
    venue2 = create_venue(offerer, siret=offerer.siren + '67890', postal_code='93000', departement_code='93')
    venue3 = create_venue(offerer, siret=offerer.siren + '54321', postal_code='93000', departement_code='93')
    offer1 = create_event_offer(venue1, event_type=EventType.ACTIVATION)
    offer2 = create_event_offer(venue2, event_type=EventType.ACTIVATION)
    offer3 = create_event_offer(venue3, event_type=EventType.ACTIVATION)
    offer4 = create_event_offer(venue3, event_type=EventType.ACTIVATION)
    stock1 = create_stock_from_offer(offer1, price=0, available=0)
    stock2 = create_stock_from_offer(offer2, price=0, available=10)
    stock3 = create_stock_from_offer(offer3, price=0, available=1)
    booking = create_booking(create_user(), stock3, venue=venue3, quantity=1)
    PcObject.check_and_save(stock1, stock2, stock3, booking, offer4)

    # when
    offers = find_activation_offers('93').all()

    # then
    assert len(offers) == 1


@clean_database
@pytest.mark.standalone
def test_find_activation_offers_returns_activation_offers_with_future_booking_limit_datetime(app):
    # given
    now = datetime.utcnow()
    five_days_ago = now - timedelta(days=5)
    next_week = now + timedelta(days=7)
    offerer = create_offerer()
    venue1 = create_venue(offerer, siret=offerer.siren + '12345', postal_code='93000', departement_code='93')
    venue2 = create_venue(offerer, siret=offerer.siren + '67890', postal_code='93000', departement_code='93')
    venue3 = create_venue(offerer, siret=offerer.siren + '54321', postal_code='93000', departement_code='93')
    offer1 = create_event_offer(venue1, event_type=EventType.ACTIVATION)
    offer2 = create_event_offer(venue2, event_type=EventType.ACTIVATION)
    offer3 = create_event_offer(venue3, event_type=EventType.ACTIVATION)
    stock1 = create_stock_from_offer(offer1, price=0, booking_limit_datetime=five_days_ago)
    stock2 = create_stock_from_offer(offer2, price=0, booking_limit_datetime=next_week)
    stock3 = create_stock_from_offer(offer3, price=0, booking_limit_datetime=None)
    PcObject.check_and_save(stock1, stock2, stock3)

    # when
    offers = find_activation_offers('93').all()

    # then
    assert len(offers) == 2
