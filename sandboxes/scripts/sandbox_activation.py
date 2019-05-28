from models import ThingType, PcObject
from tests.test_utils import create_offerer, create_venue, create_offer_with_thing_product, \
    create_stock_with_thing_offer


def save_sandbox():

    offerer = create_offerer()
    venue = create_venue(offerer, is_virtual=True, siret=None)
    offer = create_offer_with_thing_product(venue, thing_type=ThingType.ACTIVATION)
    stock = create_stock_with_thing_offer(offerer, venue, offer=offer, price=0, available=10000)
    PcObject.save(stock)
