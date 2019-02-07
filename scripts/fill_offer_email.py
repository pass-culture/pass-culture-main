from typing import List

from models import Offer, PcObject, UserOfferer, Venue, User, Offerer


def fill_booking_email(offers: List[Offer]):
    for offer in offers:
        if offer.bookingEmail:
            continue
        venue_booking_email = offer.venue.bookingEmail
        if venue_booking_email:
            offer.bookingEmail = venue_booking_email
        else:
            user_linked_to_offerer = User.query.join(UserOfferer).join(Offerer).join(Venue).join(Offer).filter(
                Offer.id == offer.id).first()
            if user_linked_to_offerer:
                offer.bookingEmail = user_linked_to_offerer.email
        PcObject.check_and_save(*offers)
