from pcapi.core.offers.models import Offer
from pcapi.models import BankInformation
from pcapi.models import StockSQLEntity
from pcapi.models import ThingType
from pcapi.models import VenueSQLEntity
from pcapi.models.offer_type import EventType
from pcapi.models.offerer import Offerer
from pcapi.models.user_sql_entity import UserSQLEntity
from pcapi.repository.user_queries import filter_users_with_at_least_one_validated_offerer_validated_user_offerer
from pcapi.sandboxes.scripts.utils.helpers import get_offer_helper
from pcapi.sandboxes.scripts.utils.helpers import get_offerer_helper
from pcapi.sandboxes.scripts.utils.helpers import get_pro_helper
from pcapi.sandboxes.scripts.utils.helpers import get_stock_helper
from pcapi.sandboxes.scripts.utils.helpers import get_venue_helper


def get_existing_pro_validated_user_with_validated_offerer_with_iban_validated_user_offerer_with_event_offer_with_no_stock():
    query = UserSQLEntity.query.filter(UserSQLEntity.validationToken == None)
    query = filter_users_with_at_least_one_validated_offerer_validated_user_offerer(query)
    query = query.join(BankInformation)
    query = query.join(VenueSQLEntity, VenueSQLEntity.managingOffererId == Offerer.id).join(Offer).filter(
        (Offer.type.in_([str(event_type) for event_type in EventType])) & \
        (~Offer.stocks.any())
    )
    user = query.first()

    for uo in user.UserOfferers:
        if uo.validationToken == None \
                and uo.offerer.validationToken == None \
                and uo.offerer.iban:
            for venue in uo.offerer.managedVenues:
                for offer in venue.offers:
                    if offer.isEvent \
                            and len(offer.stocks) == 0:
                        return {
                            "offer": get_offer_helper(offer),
                            "offerer": get_offerer_helper(uo.offerer),
                            "user": get_pro_helper(user),
                            "venue": get_venue_helper(venue)
                        }


def get_existing_pro_validated_user_with_validated_offerer_with_iban_validated_user_offerer_with_event_offer_with_stock():
    query = UserSQLEntity.query.filter(UserSQLEntity.validationToken == None)
    query = filter_users_with_at_least_one_validated_offerer_validated_user_offerer(query)
    query = query.join(BankInformation)
    query = query.join(VenueSQLEntity, VenueSQLEntity.managingOffererId == Offerer.id) \
        .join(Offer) \
        .join(StockSQLEntity) \
        .filter((StockSQLEntity.beginningDatetime != None))
    user = query.first()

    for uo in user.UserOfferers:
        if uo.validationToken == None \
                and uo.offerer.validationToken == None \
                and uo.offerer.iban:
            for venue in uo.offerer.managedVenues:
                for offer in venue.offers:
                    if offer.isEvent \
                            and offer.stocks:
                        for stock in offer.stocks:
                            if stock.beginningDatetime:
                                return {
                                    "offer": get_offer_helper(offer),
                                    "offerer": get_offerer_helper(uo.offerer),
                                    "stock": get_stock_helper(stock),
                                    "user": get_pro_helper(user),
                                    "venue": get_venue_helper(venue)
                                }


def get_existing_pro_validated_user_with_validated_offerer_with_iban_validated_user_offerer_with_thing_offer_with_stock():
    query = UserSQLEntity.query.filter(UserSQLEntity.validationToken == None)
    query = filter_users_with_at_least_one_validated_offerer_validated_user_offerer(query)
    query = query.join(BankInformation)
    query = query.join(VenueSQLEntity, VenueSQLEntity.managingOffererId == Offerer.id) \
        .join(Offer) \
        .join(Offer.stocks)
    user = query.first()

    for uo in user.UserOfferers:
        if uo.validationToken == None \
                and uo.offerer.validationToken == None \
                and uo.offerer.iban:
            for venue in uo.offerer.managedVenues:
                for offer in venue.offers:
                    if offer.isThing and offer.stocks and offer.isEditable:
                        return {
                            "offer": get_offer_helper(offer),
                            "offerer": get_offerer_helper(uo.offerer),
                            "stock": get_stock_helper(offer.stocks[0]),
                            "user": get_pro_helper(user),
                            "venue": get_venue_helper(venue)
                        }


def get_existing_pro_validated_user_with_validated_offerer_with_no_iban_validated_user_offerer_with_thing_offer_with_no_stock():
    query = UserSQLEntity.query.filter(UserSQLEntity.validationToken == None)
    query = filter_users_with_at_least_one_validated_offerer_validated_user_offerer(query)
    query = query.filter(Offerer.bankInformation == None)
    query = query.join(VenueSQLEntity).filter(VenueSQLEntity.offers.any(
        (Offer.type.in_([str(thing_type) for thing_type in ThingType])) & \
        (~Offer.stocks.any())
    ))
    user = query.first()

    for uo in user.UserOfferers:
        if uo.validationToken == None \
                and uo.offerer.validationToken == None \
                and not uo.offerer.iban:
            for venue in uo.offerer.managedVenues:
                for offer in venue.offers:
                    if offer.isThing and len(offer.stocks) == 0 and offer.isEditable:
                        return {
                            "offer": get_offer_helper(offer),
                            "offerer": get_offerer_helper(uo.offerer),
                            "user": get_pro_helper(user),
                            "venue": get_venue_helper(venue)
                        }


def get_existing_pro_validated_user_with_validated_offerer_with_no_iban_validated_user_offerer_with_event_offer():
    query = UserSQLEntity.query.filter(UserSQLEntity.validationToken == None)
    query = filter_users_with_at_least_one_validated_offerer_validated_user_offerer(query)
    query = query.filter(Offerer.bankInformation == None)
    query = query.join(VenueSQLEntity).join(Offer).filter(Offer.type.in_([str(thing_type) for thing_type in ThingType]))
    query = query.filter(VenueSQLEntity.isVirtual == False)
    user = query.first()

    for uo in user.UserOfferers:
        if uo.validationToken == None \
                and uo.offerer.validationToken == None \
                and not uo.offerer.iban:
            for venue in uo.offerer.managedVenues:
                if not venue.isVirtual:
                    for offer in venue.offers:
                        if offer.isEvent:
                            return {
                                "offer": get_offer_helper(offer),
                                "offerer": get_offerer_helper(uo.offerer),
                                "user": get_pro_helper(user),
                                "venue": get_venue_helper(venue)
                            }
