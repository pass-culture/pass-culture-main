from datetime import datetime, timedelta

import pytest

from models import Thing, PcObject, Event
from models.offer_type import EventType, ThingType
from repository.offer_queries import departement_or_national_offers, \
                                     find_activation_offers, \
                                     get_offers_for_recommendations_search, \
                                     get_active_offers_by_type
from tests.conftest import clean_database
from utils.test_utils import create_booking, \
    create_event, \
    create_event_occurrence, \
    create_event_offer, \
    create_mediation, \
    create_stock_from_event_occurrence, \
    create_thing, \
    create_thing_offer, \
    create_offerer, \
    create_stock_from_offer, \
    create_stock_with_thing_offer, \
    create_venue, \
    create_user


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
    event = create_event('Voir une pièce', is_national=True)
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
def test_get_offers_for_recommendations_search_by_one_event_type_returns_only_offers_on_events_of_that_type(app):
    # Given
    type_label = EventType.CONFERENCE_DEBAT_DEDICACE
    other_type_label = EventType.MUSIQUE

    conference_event1 = create_event('Rencontre avec Franck Lepage', event_type=type_label)
    conference_event2 = create_event('Conférence ouverte', event_type=type_label)
    concert_event = create_event('Concert de Gael Faye', event_type=other_type_label)

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

    conference_offer1 = create_event_offer(venue, conference_event1)
    conference_offer2 = create_event_offer(venue, conference_event2)
    concert_offer = create_event_offer(venue, concert_event)

    conference_event_occurrence1 = create_event_occurrence(conference_offer1)
    conference_event_occurrence2 = create_event_occurrence(conference_offer2)
    concert_event_occurrence = create_event_occurrence(concert_offer)

    conference_stock1 = create_stock_from_event_occurrence(conference_event_occurrence1)
    conference_stock2 = create_stock_from_event_occurrence(conference_event_occurrence2)
    concert_stock = create_stock_from_event_occurrence(concert_event_occurrence)

    PcObject.check_and_save(conference_stock1, conference_stock2, concert_stock)

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


@pytest.mark.standalone
@clean_database
def test_get_offers_for_recommendations_search_by_one_thing_type_returns_only_offers_on_things_of_that_type(app):
    # Given
    type_label_ok = ThingType.JEUX_VIDEO
    type_label_ko = ThingType.LIVRE_EDITION

    thing_ok1 = create_thing(thing_type=type_label_ok)
    thing_ok2 = create_thing(thing_type=type_label_ok)
    thing_ko = create_thing(thing_type=type_label_ko)
    event_ko = create_event(event_type=EventType.CINEMA)

    offerer = create_offerer()
    venue = create_venue(offerer)

    ok_offer_1 = create_thing_offer(venue, thing_ok1)
    ok_offer_2 = create_thing_offer(venue, thing_ok2)
    ko_offer = create_thing_offer(venue, thing_ko)
    ko_event_offer = create_event_offer(venue, event_ko)

    ko_event_occurrence = create_event_occurrence(ko_event_offer)

    ok_stock1 = create_stock_from_offer(ok_offer_1)
    ok_stock2 = create_stock_from_offer(ok_offer_2)
    ko_stock1 = create_stock_from_offer(ko_offer)
    ko_stock2 = create_stock_from_event_occurrence(ko_event_occurrence)

    PcObject.check_and_save(ok_stock1, ok_stock2, ko_stock1, ko_stock2)

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


def create_event_stock_and_offer_for_date(venue, date):
    event = create_event()
    offer = create_event_offer(venue, event)
    event_occurrence = create_event_occurrence(offer, beginning_datetime=date, end_datetime=date + timedelta(hours=1))
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
            [datetime(2018, 1, 6, 12, 0), datetime(2018, 1, 6, 13, 0)]
        ],
    )

    # Then
    assert ok_stock.resolvedOffer in search_result_offers
    assert ok_stock_thing.resolvedOffer in search_result_offers
    assert ko_stock_before.resolvedOffer not in search_result_offers
    assert ko_stock_after.resolvedOffer not in search_result_offers


@clean_database
@pytest.mark.standalone
def test_get_offers_for_recommendations_search_with_several_partial_keywords(app):
    # Given
    thing_ok = create_thing(thing_name='Rencontre de michel')
    thing = create_thing(thing_name='Rencontre avec jean-luc')
    event = create_event(event_name='Rencontre avec jean-mimi chelou')
    offerer = create_offerer()
    venue = create_venue(offerer)
    thing_ok_offer = create_thing_offer(venue, thing_ok)
    thing_ko_offer = create_thing_offer(venue, thing)
    event_ko_offer = create_event_offer(venue, event)
    event_ko_occurrence = create_event_occurrence(event_ko_offer)
    event_ko_stock = create_stock_from_event_occurrence(event_ko_occurrence)
    thing_ok_stock = create_stock_from_offer(thing_ok_offer)
    thing_ko_stock = create_stock_from_offer(thing_ko_offer)
    PcObject.check_and_save(event_ko_stock, thing_ok_stock, thing_ko_stock)

    # When
    offers = get_offers_for_recommendations_search(keywords='renc michel')

    # Then
    assert thing_ok_offer in offers
    assert thing_ko_offer not in offers
    assert event_ko_offer not in offers


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


@clean_database
@pytest.mark.standalone
def test_get_offers_for_recommendations_search_with_distance_less_than_1km_returns_one_offer_in_venue_with_coordonnates_that_match(app):
    # Given
    offerer75 = create_offerer(
        siren='507633576',
        city='Paris',
        postal_code='75002',
        name='LE GRAND REX PARIS',
        validation_token=None,
        iban=None,
        bic=None
    )
    venue75 = create_venue(
        offerer75,
        name='LE GRAND REX PARIS',
        address="1 BD POISSONNIERE",
        postal_code='75002',
        city="Paris",
        departement_code='75',
        is_virtual=False,
        longitude="2.4002701",
        latitude="48.8363788",
        siret="50763357600075"
    )
    venue77 = create_venue(
    offerer75,
    name='Centre Culturel Municipal Jacques Prévert',
    city="Villeparisis",
    departement_code='77',
    is_virtual=False,
    longitude="2.614391",
    latitude="48.942623",
    siret="50763357600077"
    )
    venue78 = create_venue(
        offerer75,
        name='CAC Georges Brassens',
        city="Mantes-la-jolie",
        departement_code='78',
        is_virtual=False,
        longitude="2.713513",
        latitude="48.985968",
        siret="50763357600078"
    )
    venue92 = create_venue(
        offerer75,
        name='2G – Théâtre de Gennevilliers',
        city="Gennevilliers",
        departement_code='92',
        is_virtual=False,
        longitude="2.2985554",
        latitude="48.9143444",
        siret="50763357600092"
    )

    concert_event = create_event('Concert de Gael Faye')

    concert_offer75 = create_event_offer(venue75, concert_event)
    concert_offer78 = create_event_offer(venue78, concert_event)
    concert_offer77 = create_event_offer(venue77, concert_event)
    concert_offer92 = create_event_offer(venue92, concert_event)

    concert_event_occurrence75 = create_event_occurrence(concert_offer75)
    concert_stock75 = create_stock_from_event_occurrence(concert_event_occurrence75)

    concert_event_occurrence77 = create_event_occurrence(concert_offer77)
    concert_stock77 = create_stock_from_event_occurrence(concert_event_occurrence77)

    concert_event_occurrence78 = create_event_occurrence(concert_offer78)
    concert_stock78 = create_stock_from_event_occurrence(concert_event_occurrence78)

    concert_event_occurrence92 = create_event_occurrence(concert_offer92)
    concert_stock92 = create_stock_from_event_occurrence(concert_event_occurrence92)

    PcObject.check_and_save(concert_stock75, concert_stock77, concert_stock78, concert_stock92)

    # When
    # User in Mantes-la-jolie
    offers = get_offers_for_recommendations_search(max_distance=1, longitude=2.713513, latitude=48.985968)

    # Then
    assert concert_offer75 not in offers
    assert concert_offer77 not in offers
    assert concert_offer78 in offers
    assert concert_offer92 not in offers

@clean_database
@pytest.mark.standalone
def test_get_offers_for_recommendations_search_with_all_distances_should_returns_all_offers(app):
        # Given
        offerer75 = create_offerer(
            siren='507633576',
            city='Paris',
            postal_code='75002',
            name='LE GRAND REX PARIS',
            validation_token=None,
            iban=None,
            bic=None
        )
        venue13 = create_venue(
        offerer75,
        name='Friche La Belle de Mai',
        city="Marseille",
        departement_code='13',
        is_virtual=False,
        longitude="5.3764073",
        latitude="43.303906",
        siret="50763357600013"
        )
        venue75 = create_venue(
            offerer75,
            name='LE GRAND REX PARIS',
            address="1 BD POISSONNIERE",
            postal_code='75002',
            city="Paris",
            departement_code='75',
            is_virtual=False,
            longitude="2.4002701",
            latitude="48.8363788",
            siret="50763357600075"
        )
        venue78 = create_venue(
            offerer75,
            name='CAC Georges Brassens',
            city="Mantes-la-jolie",
            departement_code='78',
            is_virtual=False,
            longitude="2.713513",
            latitude="48.985968",
            siret="50763357600078"
        )
        venue92 = create_venue(
            offerer75,
            name='2G – Théâtre de Gennevilliers',
            city="Gennevilliers",
            departement_code='92',
            is_virtual=False,
            longitude="2.2985554",
            latitude="48.9143444",
            siret="50763357600092"
        )
        venue77 = create_venue(
            offerer75,
            name='Centre Culturel Municipal Jacques Prévert',
            city="Villeparisis",
            departement_code='77',
            is_virtual=False,
            longitude="2.614391",
            latitude="48.942623",
            siret="50763357600077"
        )
        venue91 = create_venue(
            offerer75,
            name='Théâtre de Longjumeau',
            city="Longjumeau",
            departement_code='91',
            is_virtual=False,
            longitude="2.2881266",
            latitude="48.6922895",
            siret="50763357600091"
        )
        venue93 = create_venue(
        offerer75,
        name='La Salle',
        city="Aulnay Sous Bois",
        departement_code='93',
        is_virtual=False,
        longitude="2.3458074",
        latitude="48.9247067",
        siret="50763357600093"
        )
        venue94 = create_venue(
            offerer75,
            name='Centre Culturel Municipal Jacques Prévert',
            city="Cachan",
            departement_code='91',
            is_virtual=False,
            longitude="2.3231582",
            latitude="48.7914281",
            siret="50763357600094"
        )
        venue95 = create_venue(
            offerer75,
            name='EMB',
            city="Sannois",
            departement_code='95',
            is_virtual=False,
            longitude="2.2683263",
            latitude="48.976826",
            siret="50763357600095"
        )
        venue973 = create_venue(
        offerer75,
        name='Théâtre de Macouria',
        city="Cayenne",
        departement_code='973',
        is_virtual=False,
        longitude="-52.423277",
        latitude="4.9780178",
        siret="50763357600973"
        )

        concert_event = create_event('Concert de Gael Faye')

        concert_offer13 = create_event_offer(venue13, concert_event)
        concert_offer75 = create_event_offer(venue75, concert_event)
        concert_offer77 = create_event_offer(venue77, concert_event)
        concert_offer78 = create_event_offer(venue78, concert_event)
        concert_offer91 = create_event_offer(venue91, concert_event)
        concert_offer92 = create_event_offer(venue92, concert_event)
        concert_offer93 = create_event_offer(venue93, concert_event)
        concert_offer94 = create_event_offer(venue94, concert_event)
        concert_offer95 = create_event_offer(venue95, concert_event)
        concert_offer973 = create_event_offer(venue973, concert_event)

        concert_event_occurrence13 = create_event_occurrence(concert_offer13)
        concert_stock13 = create_stock_from_event_occurrence(concert_event_occurrence13)

        concert_event_occurrence91 = create_event_occurrence(concert_offer91)
        concert_stock91 = create_stock_from_event_occurrence(concert_event_occurrence91)

        concert_event_occurrence93 = create_event_occurrence(concert_offer93)
        concert_stock93 = create_stock_from_event_occurrence(concert_event_occurrence93)

        concert_event_occurrence94 = create_event_occurrence(concert_offer94)
        concert_stock94 = create_stock_from_event_occurrence(concert_event_occurrence94)

        concert_event_occurrence95 = create_event_occurrence(concert_offer95)
        concert_stock95 = create_stock_from_event_occurrence(concert_event_occurrence95)

        concert_event_occurrence973 = create_event_occurrence(concert_offer973)
        concert_stock973 = create_stock_from_event_occurrence(concert_event_occurrence973)

        PcObject.check_and_save(concert_stock13, concert_stock95, concert_stock91, concert_stock93, concert_stock94, concert_stock973 )

        # When
        # User in Mantes-la-jolie
        offers = get_offers_for_recommendations_search(max_distance=20000, longitude=2.713513, latitude=48.985968)

        # Then
        assert concert_offer13 in offers
        assert concert_offer91 in offers
        assert concert_offer93 in offers
        assert concert_offer94 in offers
        assert concert_offer95 in offers
        assert concert_offer973 in offers

@clean_database
@pytest.mark.standalone
def test_get_offers_for_recommendations_search_with_distance_less_than_20kms_returns_one_offer_in_venue_with_coordonnates_that_match_with_user_in_Paris(app):
        # Given
        offerer75 = create_offerer(
            siren='507633576',
            city='Paris',
            postal_code='75002',
            name='LE GRAND REX PARIS',
            validation_token=None,
            iban=None,
            bic=None
        )
        venue75 = create_venue(
            offerer75,
            name='LE GRAND REX PARIS',
            address="1 BD POISSONNIERE",
            postal_code='75002',
            city="Paris",
            departement_code='75',
            is_virtual=False,
            longitude="2.4002701",
            latitude="48.8363788",
            siret="50763357600075"
        )
        venue77 = create_venue(
            offerer75,
            name='Centre Culturel Municipal Jacques Prévert',
            city="Villeparisis",
            departement_code='77',
            is_virtual=False,
            longitude="2.614391",
            latitude="48.942623",
            siret="50763357600077"
        )
        venue78 = create_venue(
            offerer75,
            name='CAC Georges Brassens',
            city="Mantes-la-jolie",
            departement_code='78',
            is_virtual=False,
            longitude="2.713513",
            latitude="48.985968",
            siret="50763357600078"
        )
        venue91 = create_venue(
            offerer75,
            name='Théâtre de Orsay',
            city="Orsay",
            departement_code='91',
            is_virtual=False,
            longitude="2.1911928",
            latitude="48.7034926",
            siret="50763357600091"
        )
        venue92 = create_venue(
            offerer75,
            name='2G – Théâtre de Gennevilliers',
            city="Gennevilliers",
            departement_code='92',
            is_virtual=False,
            longitude="2.2985554",
            latitude="48.9143444",
            siret="50763357600092"
        )
        venue93 = create_venue(
        offerer75,
        name='La Salle',
        city="Aulnay Sous Bois",
        departement_code='93',
        is_virtual=False,
        longitude="2.3458074",
        latitude="48.9247067",
        siret="50763357600093"
        )
        venue95 = create_venue(
            offerer75,
            name='EMB',
            city="Sannois",
            departement_code='95',
            is_virtual=False,
            longitude="2.2683263",
            latitude="48.976826",
            siret="50763357600095"
        )
        venue94 = create_venue(
            offerer75,
            name='Centre Culturel Municipal Jacques Prévert',
            city="Cachan",
            departement_code='91',
            is_virtual=False,
            longitude="2.3231582",
            latitude="48.7914281",
            siret="50763357600094"
        )

        concert_event = create_event('Concert de Gael Faye')

        concert_offer75 = create_event_offer(venue75, concert_event)
        concert_offer77 = create_event_offer(venue77, concert_event)
        concert_offer78 = create_event_offer(venue78, concert_event)
        concert_offer91 = create_event_offer(venue91, concert_event)
        concert_offer92 = create_event_offer(venue92, concert_event)
        concert_offer93 = create_event_offer(venue93, concert_event)
        concert_offer94 = create_event_offer(venue94, concert_event)
        concert_offer95 = create_event_offer(venue95, concert_event)

        concert_event_occurrence75 = create_event_occurrence(concert_offer75)
        concert_stock75 = create_stock_from_event_occurrence(concert_event_occurrence75)

        concert_event_occurrence77 = create_event_occurrence(concert_offer77)
        concert_stock77 = create_stock_from_event_occurrence(concert_event_occurrence77)

        concert_event_occurrence78 = create_event_occurrence(concert_offer78)
        concert_stock78 = create_stock_from_event_occurrence(concert_event_occurrence78)

        concert_event_occurrence91 = create_event_occurrence(concert_offer91)
        concert_stock91 = create_stock_from_event_occurrence(concert_event_occurrence91)

        concert_event_occurrence92 = create_event_occurrence(concert_offer92)
        concert_stock92 = create_stock_from_event_occurrence(concert_event_occurrence92)

        concert_event_occurrence93 = create_event_occurrence(concert_offer93)
        concert_stock93 = create_stock_from_event_occurrence(concert_event_occurrence93)

        concert_event_occurrence94 = create_event_occurrence(concert_offer94)
        concert_stock94 = create_stock_from_event_occurrence(concert_event_occurrence94)

        concert_event_occurrence95 = create_event_occurrence(concert_offer95)
        concert_stock95 = create_stock_from_event_occurrence(concert_event_occurrence95)

        PcObject.check_and_save(concert_stock75, concert_stock77, concert_stock78, concert_offer91, concert_offer92, concert_offer93, concert_offer94, concert_offer95)

        # When
        # User in Paris
        offers = get_offers_for_recommendations_search(max_distance=20, longitude=2.4002701, latitude=48.8363788)

        # Then
        assert concert_offer75 in offers
        assert concert_offer77 in offers
        assert concert_offer78 not in offers
        assert concert_offer91 not in offers
        assert concert_offer92 in offers
        assert concert_offer93 in offers
        assert concert_offer94 in offers
        assert concert_offer95 in offers

@clean_database
@pytest.mark.standalone
def test_get_offers_for_recommendations_search_with_distance_less_than_50kms_returns_one_offer_in_venue_with_coordonnates_that_match_with_user_in_Paris(app):
        # Given
        offerer75 = create_offerer(
            siren='507633576',
            city='Paris',
            postal_code='75002',
            name='LE GRAND REX PARIS',
            validation_token=None,
            iban=None,
            bic=None
        )
        venue45 = create_venue(
            offerer75,
            name='Salle Albert Camus',
            city="Orléans",
            departement_code='45',
            is_virtual=False,
            longitude="1.9201176",
            latitude="47.9063667",
            siret="50763357600045"
        )
        venue75 = create_venue(
            offerer75,
            name='LE GRAND REX PARIS',
            address="1 BD POISSONNIERE",
            postal_code='75002',
            city="Paris",
            departement_code='75',
            is_virtual=False,
            longitude="2.4002701",
            latitude="48.8363788",
            siret="50763357600075"
        )
        venue78 = create_venue(
            offerer75,
            name='CAC Georges Brassens',
            city="Mantes-la-jolie",
            departement_code='78',
            is_virtual=False,
            longitude="2.713513",
            latitude="48.985968",
            siret="50763357600078"
        )
        venue91 = create_venue(
            offerer75,
            name='Théâtre de Orsay',
            city="Orsay",
            departement_code='91',
            is_virtual=False,
            longitude="2.1911928",
            latitude="48.7034926",
            siret="50763357600091"
        )

        concert_event = create_event('Concert de Gael Faye')

        concert_offer45 = create_event_offer(venue45, concert_event)
        concert_offer75 = create_event_offer(venue75, concert_event)
        concert_offer78 = create_event_offer(venue78, concert_event)
        concert_offer91 = create_event_offer(venue91, concert_event)

        concert_event_occurrence45 = create_event_occurrence(concert_offer45)
        concert_stock45 = create_stock_from_event_occurrence(concert_event_occurrence45)

        concert_event_occurrence75 = create_event_occurrence(concert_offer75)
        concert_stock75 = create_stock_from_event_occurrence(concert_event_occurrence75)

        concert_event_occurrence78 = create_event_occurrence(concert_offer78)
        concert_stock78 = create_stock_from_event_occurrence(concert_event_occurrence78)

        concert_event_occurrence91 = create_event_occurrence(concert_offer91)
        concert_stock91 = create_stock_from_event_occurrence(concert_event_occurrence91)

        PcObject.check_and_save(concert_stock45, concert_stock75, concert_stock78, concert_offer91)

        # When
        # User in Paris
        offers = get_offers_for_recommendations_search(max_distance=50, longitude=2.4002701, latitude=48.8363788)

        # Then
        assert concert_offer45 not in offers
        assert concert_offer75 in offers
        assert concert_offer78 in offers
        assert concert_offer91 in offers
