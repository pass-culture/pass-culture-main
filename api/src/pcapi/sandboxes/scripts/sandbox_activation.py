from pcapi.core.categories import subcategories
from pcapi.model_creators.generic_creators import create_offerer
from pcapi.model_creators.generic_creators import create_venue
from pcapi.model_creators.specific_creators import create_offer_with_thing_product
from pcapi.model_creators.specific_creators import create_stock_with_thing_offer
from pcapi.repository import repository


def save_sandbox():

    offerer = create_offerer()
    venue = create_venue(offerer, is_virtual=True, siret=None)
    offer = create_offer_with_thing_product(venue, thing_subcategory_id=subcategories.ACTIVATION_THING.id)
    stock = create_stock_with_thing_offer(offerer, venue, offer=offer, price=0, quantity=10000)
    repository.save(stock)
