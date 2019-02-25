import pytest

from models import PcObject, ApiErrors
from tests.conftest import clean_database
from tests.test_utils import create_offerer, create_venue, create_thing_offer, create_event_offer


@pytest.mark.standalone
@clean_database
def test_nOffers(app):
    # given
    offerer = create_offerer()
    venue_1 = create_venue(offerer, siret='12345678912345')
    venue_2 = create_venue(offerer, siret='67891234512345')
    venue_3 = create_venue(offerer, siret='23451234567891')
    offer_v1_1 = create_thing_offer(venue_1)
    offer_v1_2 = create_event_offer(venue_1)
    offer_v2_1 = create_event_offer(venue_2)
    offer_v2_2 = create_event_offer(venue_2)
    offer_v3_1 = create_thing_offer(venue_3)
    PcObject.check_and_save(offer_v1_1, offer_v1_2, offer_v2_1, offer_v2_2, offer_v3_1)

    # when
    n_offers = offerer.nOffers

    # then
    assert n_offers == 5


@pytest.mark.standalone
@clean_database
def test_offerer_can_have_null_address(app):
    # given
    offerer = create_offerer(address=None)

    try:
        # when
        PcObject.check_and_save(offerer)
    except ApiErrors:
        # then
        assert False
