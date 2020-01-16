from models import ThingType, User
from tests.model_creators.generic_creators import create_booking, create_offerer, create_venue
from tests.model_creators.specific_creators import create_stock_with_thing_offer, create_offer_with_thing_product
from utils.logger import logger

def create_industrial_activation_offers():
    logger.info('create_industrial_activation_offers')

    activated_user = User.query.filter_by(canBookFreeOffers=True).first()
    offerer = create_offerer()
    venue = create_venue(offerer, is_virtual=True, siret=None)
    offer = create_offer_with_thing_product(venue, thing_type=ThingType.ACTIVATION)
    stock = create_stock_with_thing_offer(offerer, venue, offer=offer, price=0, available=10000)

    booking = create_booking(user=activated_user, stock=stock, token='ACTIVA', venue=venue)

    Repository.save(booking, stock)




