import pytest

from models import Thing, PcObject, Event
from repository.offer_queries import departement_or_national_offers
from tests.conftest import clean_database
from utils.test_utils import create_thing, create_event, create_thing_offer, create_venue, create_offerer, \
    create_event_offer


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