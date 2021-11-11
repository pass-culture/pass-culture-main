import datetime

import pcapi.core.bookings.factories as bookings_factories
from pcapi.core.educational.models import EducationalBookingStatus
from pcapi.core.offers import factories as offers_factories
from pcapi.sandboxes.scripts.utils.helpers import get_booking_helper
from pcapi.sandboxes.scripts.utils.helpers import get_pro_helper


def get_existing_pro_validated_user_with_validated_offerer_with_validated_user_offerer_with_thing_offer_with_stock_with_not_used_booking():
    user_offerer = offers_factories.UserOffererFactory()
    venue = offers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
    offer = offers_factories.ThingOfferFactory(venue=venue, isActive=True)
    stock = offers_factories.StockFactory(offer=offer)
    booking = bookings_factories.IndividualBookingFactory(stock=stock, isUsed=False)

    return {
        "booking": get_booking_helper(booking),
        "user": get_pro_helper(user_offerer.user),
    }


def get_existing_pro_validated_user_with_validated_offerer_with_validated_user_offerer_with_eac_offer_with_stock_with_not_used_booking_validated_by_principal():
    user_offerer = offers_factories.UserOffererFactory()
    booking = bookings_factories.EducationalBookingFactory(
        dateCreated=datetime.datetime.utcnow() - datetime.timedelta(days=5),
        stock__offer__venue__managingOfferer=user_offerer.offerer,
        educationalBooking__status=EducationalBookingStatus.USED_BY_INSTITUTE,
    )

    return {
        "booking": get_booking_helper(booking),
        "user": get_pro_helper(user_offerer.user),
    }
