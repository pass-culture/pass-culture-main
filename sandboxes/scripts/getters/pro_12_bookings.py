from models.booking_sql_entity import BookingSQLEntity
from models.offer import Offer
from models.offerer import Offerer
from models.stock_sql_entity import StockSQLEntity
from models.user_sql_entity import UserSQLEntity
from models.user_offerer import UserOfferer
from models import VenueSQLEntity
from sandboxes.scripts.utils.helpers import get_booking_helper, \
    get_offer_helper, \
    get_offerer_helper, \
    get_stock_helper, \
    get_pro_helper, \
    get_venue_helper

def get_existing_pro_validated_user_with_validated_offerer_with_booking():
    query = BookingSQLEntity.query.join(StockSQLEntity) \
                         .join(Offer) \
                         .join(VenueSQLEntity) \
                         .join(Offerer) \
                         .join(UserOfferer) \
                         .filter(
                            (Offerer.validationToken == None) & \
                            (UserOfferer.validationToken == None)
                         ) \
                         .join(UserSQLEntity) \
                         .filter(UserSQLEntity.validationToken == None)

    booking = query.first()
    stock = booking.stock
    offer = stock.offer
    venue = offer.venue
    offerer = venue.managingOfferer
    user = [
        uo.user
        for uo in offerer.UserOfferers
        if uo.user.validationToken == None
    ][0]
    return {
        "booking": get_booking_helper(booking),
        "offer": get_offer_helper(offer),
        "offerer": get_offerer_helper(offerer),
        "stock": get_stock_helper(stock),
        "user": get_pro_helper(user),
        "venue": get_venue_helper(venue)
    }
