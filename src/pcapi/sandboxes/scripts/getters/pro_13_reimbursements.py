from pcapi.core.bookings.models import Booking
from pcapi.core.offerers.offerer import Offerer
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import Stock
from pcapi.core.users.models import User
from pcapi.models import Venue
from pcapi.models.payment import Payment
from pcapi.models.user_offerer import UserOfferer
from pcapi.sandboxes.scripts.utils.helpers import get_booking_helper
from pcapi.sandboxes.scripts.utils.helpers import get_offer_helper
from pcapi.sandboxes.scripts.utils.helpers import get_offerer_helper
from pcapi.sandboxes.scripts.utils.helpers import get_payment_helper
from pcapi.sandboxes.scripts.utils.helpers import get_pro_helper
from pcapi.sandboxes.scripts.utils.helpers import get_stock_helper
from pcapi.sandboxes.scripts.utils.helpers import get_venue_helper


def get_existing_pro_validated_user_with_validated_offerer_with_reimbursement():
    query = (
        Payment.query.join(Booking)
        .join(Stock)
        .join(Offer)
        .join(Venue)
        .join(Offerer)
        .join(UserOfferer)
        .filter((Offerer.validationToken == None) & (UserOfferer.validationToken == None))
        .join(User)
        .filter(User.validationToken == None)
    )

    payment = query.first()
    booking = payment.booking
    stock = booking.stock
    offer = stock.offer
    venue = offer.venue
    offerer = venue.managingOfferer
    user = [uo.user for uo in offerer.UserOfferers if uo.user.validationToken == None][0]
    return {
        "booking": get_booking_helper(booking),
        "offer": get_offer_helper(offer),
        "offerer": get_offerer_helper(offerer),
        "payment": get_payment_helper(payment),
        "stock": get_stock_helper(stock),
        "user": get_pro_helper(user),
        "venue": get_venue_helper(venue),
    }
