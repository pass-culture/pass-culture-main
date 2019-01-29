import pytest

from models.pc_object import PcObject
from repository.keywords_queries import get_keywords_analyzer
from tests.conftest import clean_database
from utils.test_utils import create_event, \
    create_event_offer, \
    create_offerer, \
    create_venue

@clean_database
@pytest.mark.standalone
def test_get_keywords_analyzer(app):
    # given
    event_name = "Rencontre avec Jacques Nuance"
    event = create_event(event_name=event_name)
    offerer_name = "L'atelier du nuage"
    offerer = create_offerer(name=offerer_name)
    venue = create_venue(offerer, name="Le nuage magique")
    offer = create_event_offer(venue, event)
    PcObject.check_and_save(offer)

    # when
    keywords_analyzer = get_keywords_analyzer(offer, 'nua')

    # then
    assert keywords_analyzer['Event_name'] == event_name
    assert keywords_analyzer['Event_description'] is False
    assert keywords_analyzer['Thing_name'] is False
    assert keywords_analyzer['Thing_description'] is False
    assert keywords_analyzer['Offerer_name'] == offerer_name
    assert keywords_analyzer['Venue_name'] is False
