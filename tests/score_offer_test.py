from unittest.mock import patch

from models import Offer, Event, Mediation, Stock, Thing
from recommendations_engine.offers import score_offer


def test_score_offer_return_none_if_no_mediation_nor_thumbCount():
    # given
    offer = Offer()
    offer.mediations = []
    offer.event = Event()
    offer.event.thumbCount = 0

    # when
    score = score_offer(offer)

    # then
    assert score is None


@patch('recommendations_engine.offers.specific_score_event')
def test_score_offer_return_none_if_specific_score_event_is_none(specific_score_event):
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
def test_score_offer_return_27_for_an_event(specific_score_event, randint):
    # given
    specific_score_event.return_value = 4
    randint.return_value = 3
    offer = Offer()
    offer.mediations = [Mediation()]
    offer.event = Event()

    # when
    score = score_offer(offer)

    # then
    assert score == 27


@patch('recommendations_engine.offers.feature_paid_offers_enabled')
def test_score_offer_return_none_given_a_paid_offer_if_feature_is_disabled(feature_paid_offers_enabled):
    # given
    stock = Stock()
    stock.price = 100

    offer = Offer()
    offer.stocks = [stock]
    offer.thing = Thing()
    offer.thing.thumbCount = 1
    feature_paid_offers_enabled.return_value = False

    # when
    score = score_offer(offer)

    # then
    assert score is None


@patch('recommendations_engine.offers.randint')
@patch('recommendations_engine.offers.feature_paid_offers_enabled')
def test_score_offer_return_a_score_given_a_paid_offer_if_feature_is_enabled(feature_paid_offers_enabled, randint):
    # given
    randint.return_value = 4
    stock = Stock()
    stock.price = 100

    offer = Offer()
    offer.stocks = [stock]
    offer.thing = Thing()
    offer.thing.thumbCount = 1
    feature_paid_offers_enabled.return_value = True

    # when
    score = score_offer(offer)

    # then
    assert score == 4


@patch('recommendations_engine.offers.randint')
@patch('recommendations_engine.offers.feature_paid_offers_enabled')
def test_score_offer_return_a_score_given_a_free_offer_if_feature_is_disabled(feature_paid_offers_enabled, randint):
    # given
    randint.return_value = 4
    stock = Stock()
    stock.price = 0

    offer = Offer()
    offer.stocks = [stock]
    offer.thing = Thing()
    offer.thing.thumbCount = 1
    feature_paid_offers_enabled.return_value = False

    # when
    score = score_offer(offer)

    # then
    assert score == 4
