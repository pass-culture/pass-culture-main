from pcapi.core.bookings.models import Booking
from pcapi.core.offers.models import OfferSQLEntity
from pcapi.models.offerer import Offerer
from pcapi.models.payment import Payment
from pcapi.models.stock_sql_entity import StockSQLEntity
from pcapi.models.user_offerer import UserOfferer
from pcapi.models.user_sql_entity import UserSQLEntity
from pcapi.models import VenueSQLEntity
from pcapi.sandboxes.scripts.utils.helpers import get_booking_helper, \
    get_offer_helper, \
    get_offerer_helper, \
    get_payment_helper, \
    get_stock_helper, \
    get_pro_helper, \
    get_venue_helper


def get_existing_pro_validated_user_with_validated_offerer_with_reimbursement():
    query = Payment.query.join(Booking) \
        .join(StockSQLEntity) \
        .join(OfferSQLEntity) \
        .join(VenueSQLEntity) \
        .join(Offerer) \
        .join(UserOfferer) \
        .filter(
        (Offerer.validationToken == None) & \
        (UserOfferer.validationToken == None)
    ) \
        .join(UserSQLEntity) \
        .filter(UserSQLEntity.validationToken == None)

    payment = query.first()
    booking = payment.booking
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
        "payment": get_payment_helper(payment),
        "stock": get_stock_helper(stock),
        "user": get_pro_helper(user),
        "venue": get_venue_helper(venue)
    }
