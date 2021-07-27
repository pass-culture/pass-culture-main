import pcapi.core.bookings.factories as bookings_factories
from pcapi.core.offers import factories as offers_factories
from pcapi.sandboxes.scripts.utils.helpers import get_booking_helper
from pcapi.sandboxes.scripts.utils.helpers import get_pro_helper


def get_existing_pro_validated_user_with_validated_offerer_with_validated_user_offerer_with_thing_offer_with_stock_with_not_used_booking():
    user_offerer = offers_factories.UserOffererFactory(
        validationToken=None,
        offerer__validationToken=None,
        user__validationToken=None,
    )
    venue = offers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
    offer = offers_factories.ThingOfferFactory(venue=venue, isActive=True)
    stock = offers_factories.StockFactory(offer=offer)
    booking = bookings_factories.BookingFactory(stock=stock, isUsed=False)

    return {
        "booking": get_booking_helper(booking),
        "user": get_pro_helper(user_offerer.user),
    }
