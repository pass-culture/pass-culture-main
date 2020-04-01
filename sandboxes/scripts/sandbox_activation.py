from models import ThingType
from repository import repository
from tests.model_creators.generic_creators import create_offerer, create_venue
from tests.model_creators.specific_creators import create_stock_with_thing_offer, create_offer_with_thing_product


def save_sandbox():

    offerer = create_offerer()
    venue = create_venue(offerer, is_virtual=True, siret=None)
    offer = create_offer_with_thing_product(venue, thing_type=ThingType.ACTIVATION)
    stock = create_stock_with_thing_offer(offerer, venue, offer=offer, price=0, quantity=10000)
    repository.save(stock)
