from unittest.mock import patch

from models import Offer, Event, Mediation
from recommendations_engine.offers import score_offer
from tests.test_utils import create_mediation


def test_score_offer_returns_none_if_no_mediation_nor_thumbCount():
    # given
    offer = Offer()
    offer.mediations = []
    offer.event = Event()
    offer.event.thumbCount = 0

    # when
    score = score_offer(offer)

    # then
    assert score is None


def test_score_offer_returns_none_if_no_active_mediation_nor_thumbCount():
    # given
    offer = Offer()
    offer.mediations = [
        create_mediation(offer, is_active=False),
        create_mediation(offer, is_active=False)
    ]
    offer.event = Event()
    offer.event.thumbCount = 0

    # when
    score = score_offer(offer)

    # then
    assert score is None


@patch('recommendations_engine.offers.specific_score_event')
def test_score_offer_returns_none_if_specific_score_event_is_none(specific_score_event):
    # given
    specific_score_event.return_value = None
    offer = Offer()
    offer.mediations = [Mediation()]
    offer.event = Event()

    # when
    score = score_offer(offer)

    # then
    assert score is None


@patch('recommendations_engine.offers.randint')
@patch('recommendations_engine.offers.specific_score_event')
def test_score_offer_returns_27_for_an_event(specific_score_event, randint):
    # given
    specific_score_event.return_value = 4
    randint.return_value = 3
    offer = Offer()
    offer.mediations = [create_mediation(offer, is_active=True)]
    offer.event = Event()

    # when
    score = score_offer(offer)

    # then
    assert score == 27
