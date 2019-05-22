from models.booking import Booking
from models.offer import Offer
from models.offerer import Offerer
from models.stock import Stock
from models.user import User
from models.venue import Venue
from repository.user_queries import filter_users_with_at_least_one_validated_offerer_validated_user_offerer
from sandboxes.scripts.utils.helpers import get_booking_helper, \
    get_offer_helper, \
    get_offerer_helper, \
    get_stock_helper, \
    get_user_helper, \
    get_venue_helper

def get_existing_pro_validated_user_with_validated_offerer_with_booking():
    query = User.query.filter(User.validationToken == None)
    query = filter_users_with_at_least_one_validated_offerer_validated_user_offerer(query)
    query = query.join(Venue, Venue.managingOffererId == Offerer.id) \
        .join(Offer) \
        .join(Stock) \
        .join(Booking)
    user = query.first()

    for uo in user.UserOfferers:
        if uo.validationToken is None \
                and uo.offerer.validationToken is None \
                and uo.offerer.iban:
            for venue in uo.offerer.managedVenues:
                for offer in venue.offers:
                    if offer.stocks:
                        for stock in offer.stocks:
                            if stock.bookings:
                                booking = stock.bookings[0]
                                return {
                                    "booking": get_booking_helper(booking),
                                    "offer": get_offer_helper(offer),
                                    "offerer": get_offerer_helper(uo.offerer),
                                    "stock": get_stock_helper(stock),
                                    "user": get_user_helper(user),
                                    "venue": get_venue_helper(venue)
                                }
