import pytest

from models.pc_object import PcObject
from repository.keywords_queries import get_keywords_analyzer
from tests.conftest import clean_database
from tests.test_utils import create_product_with_Event_type, \
    create_offer_with_event_product, \
    create_offerer, \
    create_venue


@clean_database
@pytest.mark.standalone
def test_get_keywords_analyzer(app):
    # given
    event_name = "Rencontre avec Jacques Nuance"
    product_event = create_product_with_Event_type(event_name=event_name)
    offerer_name = "L'atelier du nuage"
    offerer = create_offerer(name=offerer_name)
    venue = create_venue(offerer, name="Le nuage magique")
    offer = create_offer_with_event_product(venue=venue, product=product_event)
    PcObject.check_and_save(offer)

    # when
    keywords_analyzer = get_keywords_analyzer(offer, 'nua')

    # then
    assert keywords_analyzer['Product_description'] is False
    assert keywords_analyzer['Product_name'] is False
    assert keywords_analyzer['Offerer_name'] is False
    assert keywords_analyzer['Venue_name'] is False
