from datetime import datetime, timedelta

from models import PcObject, ThingType
from models.activity import load_activity
from repository.stock_queries import find_stocks_of_finished_events_when_no_recap_sent, find_online_activation_stock
from tests.conftest import clean_database
from tests.model_creators.generic_creators import create_offerer, create_venue
from tests.model_creators.specific_creators import create_stock_from_event_occurrence, create_stock_from_offer, \
    create_offer_with_thing_product, create_offer_with_event_product, create_event_occurrence


@clean_database
def test_find_stocks_of_finished_events_when_no_recap_sent(app):
    # Given
    offerer = create_offerer()
    venue = create_venue(offerer)
    offer = create_offer_with_event_product(venue)
    thing_offer = create_offer_with_thing_product(venue)
    event_occurrence_past = create_event_occurrence(offer, beginning_datetime=datetime.utcnow() - timedelta(hours=48),
                                                    end_datetime=datetime.utcnow() - timedelta(hours=46))
    event_occurrence_past_2 = create_event_occurrence(offer, beginning_datetime=datetime.utcnow() - timedelta(hours=10),
                                                      end_datetime=datetime.utcnow() - timedelta(hours=2))
    event_occurrence_future = create_event_occurrence(offer, beginning_datetime=datetime.utcnow() + timedelta(hours=46),
                                                      end_datetime=datetime.utcnow() + timedelta(hours=48))
    stock_past = create_stock_from_event_occurrence(event_occurrence_past)
    stock_soft_deleted = create_stock_from_event_occurrence(event_occurrence_past, soft_deleted=True)
    stock_future = create_stock_from_event_occurrence(event_occurrence_future)
    stock_thing = create_stock_from_offer(thing_offer)
    stock_recap_sent = create_stock_from_event_occurrence(event_occurrence_past_2, recap_sent=True)
    PcObject.save(stock_past, stock_future, stock_thing, stock_soft_deleted, stock_recap_sent)

    # When
    stocks = find_stocks_of_finished_events_when_no_recap_sent().all()

    # Then
    assert stock_past in stocks
    assert stock_future not in stocks
    assert stock_thing not in stocks
    assert stock_soft_deleted not in stocks


@clean_database
def test_create_stock_triggers_insert_activities(app):
    # Given
    offerer = create_offerer()
    venue = create_venue(offerer)
    thing_offer = create_offer_with_thing_product(venue)
    stock = create_stock_from_offer(thing_offer)

    # When
    PcObject.save(stock)

    # Then
    activities = load_activity().query.all()
    assert len(activities) == 4
    assert {"offerer", "venue", "offer", "stock"} == set(
        [a.table_name for a in activities]
    )
    assert {"insert"} == set([a.verb for a in activities])


@clean_database
def test_find_online_activation_stock(app):
    # given
    offerer = create_offerer(siren='123456789', name='pass Culture')
    venue_online = create_venue(offerer, siret=None, is_virtual=True)
    venue_physical = create_venue(offerer, siret='12345678912345', is_virtual=False)
    activation_offer = create_offer_with_thing_product(venue_online, thing_type=ThingType.ACTIVATION)
    other_thing_offer = create_offer_with_thing_product(venue_physical, thing_type=ThingType.ACTIVATION)
    event_offer = create_offer_with_event_product(venue_physical)
    activation_stock = create_stock_from_offer(activation_offer, available=200, price=0)
    other_thing_stock = create_stock_from_offer(other_thing_offer, available=100, price=10)
    event_stock = create_stock_from_offer(event_offer, available=50, price=20)

    PcObject.save(other_thing_stock, activation_stock, event_stock)

    # when
    stock = find_online_activation_stock()

    # then
    assert stock.offer.venue.isVirtual == True
    assert stock.offer.type == 'ThingType.ACTIVATION'
    assert stock.available == 200
    assert stock.price == 0
