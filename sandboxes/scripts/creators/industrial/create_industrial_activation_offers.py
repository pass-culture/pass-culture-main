from models import ThingType, PcObject, User
from tests.test_utils import create_offerer, create_venue, create_offer_with_thing_product, \
    create_stock_with_thing_offer, create_booking
from utils.logger import logger

def create_industrial_activation_offers():
    logger.info('create_industrial_activation_offers')

    activated_user = User.query.filter_by(canBookFreeOffers=True).first()
    offerer = create_offerer()
    venue = create_venue(offerer, is_virtual=True, siret=None)
    offer = create_offer_with_thing_product(venue, thing_type=ThingType.ACTIVATION)
    stock = create_stock_with_thing_offer(offerer, venue, offer=offer, price=0, available=10000)

    booking = create_booking(user=activated_user, stock=stock, venue=venue, token='ACTIVA')

    PcObject.save(booking, stock)




