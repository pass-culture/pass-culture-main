from pcapi.core.offers.models import OfferSQLEntity
from pcapi.models import Offerer
from pcapi.models import ThingType
from pcapi.models.offer_type import EventType
from pcapi.models.user_sql_entity import UserSQLEntity
from pcapi.models import VenueSQLEntity
from pcapi.repository.offerer_queries import keep_offerers_with_at_least_one_physical_venue
from pcapi.repository.user_queries import filter_users_with_at_least_one_validated_offerer_validated_user_offerer
from pcapi.sandboxes.scripts.utils.helpers import get_offer_helper, \
    get_offerer_helper, \
    get_pro_helper, \
    get_venue_helper


def get_existing_pro_validated_user_with_at_least_one_visible_offer():
    query = UserSQLEntity.query.filter(UserSQLEntity.validationToken == None)
    query = filter_users_with_at_least_one_validated_offerer_validated_user_offerer(query)
    query = query.join(VenueSQLEntity, VenueSQLEntity.managingOffererId == Offerer.id).join(OfferSQLEntity)
    user = query.first()

    for uo in user.UserOfferers:
        if uo.validationToken == None and uo.offerer.validationToken == None:
            for venue in uo.offerer.managedVenues:
                if venue.offers:
                    offer = venue.offers[0]
                    return {
                        "offer": get_offer_helper(offer),
                        "user": get_pro_helper(user)
                    }


def get_existing_pro_validated_user_with_validated_offerer_validated_user_offerer_with_physical_venue():
    query = UserSQLEntity.query.filter(UserSQLEntity.validationToken == None)
    query = filter_users_with_at_least_one_validated_offerer_validated_user_offerer(query)
    query = keep_offerers_with_at_least_one_physical_venue(query)
    user = query.first()

    for uo in user.UserOfferers:
        if uo.validationToken == None and uo.offerer.validationToken == None:
            for venue in uo.offerer.managedVenues:
                if not venue.isVirtual:
                    return {
                        "offerer": get_offerer_helper(uo.offerer),
                        "user": get_pro_helper(user),
                        "venue": get_venue_helper(venue)
                    }


def get_existing_pro_validated_user_with_validated_offerer_validated_user_offerer_with_virtual_venue():
    query = UserSQLEntity.query.filter(UserSQLEntity.validationToken == None)
    query = filter_users_with_at_least_one_validated_offerer_validated_user_offerer(query)
    user = query.first()

    for uo in user.UserOfferers:
        if uo.validationToken == None and uo.offerer.validationToken == None:
            for venue in uo.offerer.managedVenues:
                if venue.isVirtual:
                    return {
                        "offerer": get_offerer_helper(uo.offerer),
                        "user": get_pro_helper(user),
                        "venue": get_venue_helper(venue)
                    }


def get_existing_pro_validated_user_with_validated_offerer_validated_user_offerer_with_thing_offer():
    query = UserSQLEntity.query.filter(UserSQLEntity.validationToken == None)
    query = filter_users_with_at_least_one_validated_offerer_validated_user_offerer(query)
    query = query.join(VenueSQLEntity).join(OfferSQLEntity).filter(OfferSQLEntity.type.in_([str(thing_type) for thing_type in ThingType]))
    user = query.first()

    for uo in user.UserOfferers:
        if uo.validationToken == None and uo.offerer.validationToken == None:
            for venue in uo.offerer.managedVenues:
                for offer in venue.offers:
                    if offer.isThing:
                        return {
                            "offer": get_offer_helper(offer),
                            "offerer": get_offerer_helper(uo.offerer),
                            "user": get_pro_helper(user),
                            "venue": get_venue_helper(venue)
                        }

def get_existing_pro_validated_user_with_validated_offerer_validated_user_offerer_with_event_offer():
    query = UserSQLEntity.query.filter(UserSQLEntity.validationToken == None)
    query = filter_users_with_at_least_one_validated_offerer_validated_user_offerer(query)
    query = query.join(VenueSQLEntity).join(OfferSQLEntity).filter(OfferSQLEntity.type.in_([str(event_type) for event_type in EventType]))
    user = query.first()

    for uo in user.UserOfferers:
        if uo.validationToken == None and uo.offerer.validationToken == None:
            for venue in uo.offerer.managedVenues:
                for offer in venue.offers:
                    if offer.isEvent:
                        return {
                            "offer": get_offer_helper(offer),
                            "offerer": get_offerer_helper(uo.offerer),
                            "user": get_pro_helper(user),
                            "venue": get_venue_helper(venue)
                        }
