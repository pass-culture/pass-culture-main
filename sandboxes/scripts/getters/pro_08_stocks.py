from models import BankInformation, Stock

from models.offer import Offer
from models.offerer import Offerer

from models.user import User
from models.venue import Venue
from repository.user_queries import filter_users_with_at_least_one_validated_offerer_validated_user_offerer
from sandboxes.scripts.utils.helpers import get_offer_helper, \
    get_offerer_helper, \
    get_stock_helper, \
    get_user_helper, \
    get_venue_helper


def get_existing_pro_validated_user_with_validated_offerer_with_iban_validated_user_offerer_with_event_offer_with_no_stock():
    query = User.query.filter(User.validationToken == None)
    query = filter_users_with_at_least_one_validated_offerer_validated_user_offerer(query)
    query = query.join(BankInformation)
    query = query.join(Venue, Venue.managingOffererId == Offerer.id).join(Offer).filter(
        (Offer.eventId != None) & \
        (~Offer.stocks.any())
    )
    user = query.first()

    for uo in user.UserOfferers:
        if uo.validationToken == None \
                and uo.offerer.validationToken == None \
                and uo.offerer.iban:
            for venue in uo.offerer.managedVenues:
                for offer in venue.offers:
                    if isinstance(offer.eventOrThing, Event) \
                            and len(offer.stocks) == 0:
                        return {
                            "offer": get_offer_helper(offer),
                            "offerer": get_offerer_helper(uo.offerer),
                            "user": get_user_helper(user),
                            "venue": get_venue_helper(venue)
                        }


def get_existing_pro_validated_user_with_validated_offerer_with_iban_validated_user_offerer_with_event_offer_with_stock():
    query = User.query.filter(User.validationToken == None)
    query = filter_users_with_at_least_one_validated_offerer_validated_user_offerer(query)
    query = query.join(BankInformation)
    query = query.join(Venue, Venue.managingOffererId == Offerer.id) \
        .join(Offer) \
        .join(Stock) \
        .filter((Stock.beginningDatetime != None) & (Stock.endDatetime != None))
    user = query.first()

    for uo in user.UserOfferers:
        if uo.validationToken == None \
                and uo.offerer.validationToken == None \
                and uo.offerer.iban:
            for venue in uo.offerer.managedVenues:
                for offer in venue.offers:
                    if isinstance(offer.eventOrThing, Event) \
                            and offer.stocks:
                        for stock in offer.stocks:
                            if stock.beginningDatetime and stock.endDatetime:
                                return {
                                    "offer": get_offer_helper(offer),
                                    "offerer": get_offerer_helper(uo.offerer),
                                    "stock": get_stock_helper(stock),
                                    "user": get_user_helper(user),
                                    "venue": get_venue_helper(venue)
                                }


def get_existing_pro_validated_user_with_validated_offerer_with_iban_validated_user_offerer_with_thing_offer_with_stock():
    query = User.query.filter(User.validationToken == None)
    query = filter_users_with_at_least_one_validated_offerer_validated_user_offerer(query)
    query = query.join(BankInformation)
    query = query.join(Venue, Venue.managingOffererId == Offerer.id) \
        .join(Offer) \
        .join(Offer.stocks)
    user = query.first()

    for uo in user.UserOfferers:
        if uo.validationToken == None \
                and uo.offerer.validationToken == None \
                and uo.offerer.iban:
            for venue in uo.offerer.managedVenues:
                for offer in venue.offers:
                    if isinstance(offer.eventOrThing, Thing) \
                            and offer.stocks:
                        return {
                            "offer": get_offer_helper(offer),
                            "offerer": get_offerer_helper(uo.offerer),
                            "stock": get_stock_helper(offer.stocks[0]),
                            "user": get_user_helper(user),
                            "venue": get_venue_helper(venue)
                        }


def get_existing_pro_validated_user_with_validated_offerer_with_no_iban_validated_user_offerer_with_thing_offer_with_no_stock():
    query = User.query.filter(User.validationToken == None)
    query = filter_users_with_at_least_one_validated_offerer_validated_user_offerer(query)
    query = query.filter(Offerer.bankInformation == None)
    query = query.join(Venue).filter(Venue.offers.any(
        (Offer.thingId != None) & \
        (~Offer.stocks.any())
    ))
    user = query.first()

    for uo in user.UserOfferers:
        if uo.validationToken == None \
                and uo.offerer.validationToken == None \
                and not uo.offerer.iban:
            for venue in uo.offerer.managedVenues:
                for offer in venue.offers:
                    if offer.thingId and len(offer.stocks) == 0:
                        return {
                            "offer": get_offer_helper(offer),
                            "offerer": get_offerer_helper(uo.offerer),
                            "user": get_user_helper(user),
                            "venue": get_venue_helper(venue)
                        }


def get_existing_pro_validated_user_with_validated_offerer_with_no_iban_validated_user_offerer_with_event_offer():
    query = User.query.filter(User.validationToken == None)
    query = filter_users_with_at_least_one_validated_offerer_validated_user_offerer(query)
    query = query.filter(Offerer.bankInformation == None)
    query = query.join(Venue).join(Offer).filter(Offer.eventId != None)
    user = query.first()

    for uo in user.UserOfferers:
        if uo.validationToken == None \
                and uo.offerer.validationToken == None \
                and not uo.offerer.iban:
            for venue in uo.offerer.managedVenues:
                if not venue.isVirtual:
                    for offer in venue.offers:
                        if isinstance(offer.eventOrThing, Event):
                            return {
                                "offer": get_offer_helper(offer),
                                "offerer": get_offerer_helper(uo.offerer),
                                "user": get_user_helper(user),
                                "venue": get_venue_helper(venue)
                            }
