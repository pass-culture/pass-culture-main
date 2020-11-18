from pcapi.core.bookings.models import Booking
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import StockSQLEntity
from pcapi.models import VenueSQLEntity
from pcapi.models.offerer import Offerer
from pcapi.models.user_offerer import UserOfferer
from pcapi.models.user_sql_entity import UserSQLEntity
from pcapi.sandboxes.scripts.utils.helpers import get_booking_helper
from pcapi.sandboxes.scripts.utils.helpers import get_offer_helper
from pcapi.sandboxes.scripts.utils.helpers import get_offerer_helper
from pcapi.sandboxes.scripts.utils.helpers import get_pro_helper
from pcapi.sandboxes.scripts.utils.helpers import get_stock_helper
from pcapi.sandboxes.scripts.utils.helpers import get_venue_helper


def get_existing_pro_validated_user_with_validated_offerer_with_booking():
    query = (
        Booking.query.join(StockSQLEntity)
        .join(Offer)
        .join(VenueSQLEntity)
        .join(Offerer)
        .join(UserOfferer)
        .filter((Offerer.validationToken == None) & (UserOfferer.validationToken == None))
        .join(UserSQLEntity)
        .filter(UserSQLEntity.validationToken == None)
    )

    booking = query.first()
    stock = booking.stock
    offer = stock.offer
    venue = offer.venue
    offerer = venue.managingOfferer
    user = [uo.user for uo in offerer.UserOfferers if uo.user.validationToken == None][0]
    return {
        "booking": get_booking_helper(booking),
        "offer": get_offer_helper(offer),
        "offerer": get_offerer_helper(offerer),
        "stock": get_stock_helper(stock),
        "user": get_pro_helper(user),
        "venue": get_venue_helper(venue),
    }
