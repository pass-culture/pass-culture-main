from models import ThingType
from models.activity import load_activity
from repository import repository
from repository.stock_queries import find_online_activation_stock
from tests.conftest import clean_database
from tests.model_creators.generic_creators import create_offerer, create_venue
from tests.model_creators.specific_creators import create_stock_from_offer, \
    create_offer_with_thing_product, create_offer_with_event_product


@clean_database
def test_create_stock_triggers_insert_activities(app):
    # Given
    offerer = create_offerer()
    venue = create_venue(offerer)
    thing_offer = create_offer_with_thing_product(venue)
    stock = create_stock_from_offer(thing_offer)

    # When
    repository.save(stock)

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

    repository.save(other_thing_stock, activation_stock, event_stock)

    # when
    stock = find_online_activation_stock()

    # then
    assert stock.offer.venue.isVirtual == True
    assert stock.offer.type == 'ThingType.ACTIVATION'
    assert stock.available == 200
    assert stock.price == 0
