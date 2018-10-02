""" repository offer queries """
import pytest

from models import Thing, PcObject, Event
from models.offer_type import EventType
from repository.offer_queries import departement_or_national_offers, \
                                     get_offers_for_recommendations_search
from tests.conftest import clean_database
from utils.test_utils import create_event, \
                             create_event_occurrence, \
                             create_event_offer, \
                             create_stock_from_event_occurrence, \
                             create_thing, \
                             create_thing_offer, \
                             create_offerer, \
                             create_venue

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
def test_type_search(app):
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

    conference_stock = create_stock_from_event_occurrence(
        conference_event_occurrence
    )
    concert_stock = create_stock_from_event_occurrence(
        concert_event_occurrence 
    )


    PcObject.check_and_save(conference_stock, concert_stock)

    offers = get_offers_for_recommendations_search(
        type_labels=[
            type_label
        ],
    )

    assert conference_offer in offers
