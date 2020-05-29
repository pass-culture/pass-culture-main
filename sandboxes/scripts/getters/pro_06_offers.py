from models.offer import Offer
from models.user_sql_entity import UserSQLEntity
from models import VenueSQLEntity
from repository.user_queries import filter_users_with_at_least_one_validated_offerer_validated_user_offerer
from sandboxes.scripts.utils.helpers import get_offer_helper, get_user_helper

def get_existing_pro_validated_user_with_at_least_one_visible_activated_offer():
    query = UserSQLEntity.query.filter(UserSQLEntity.validationToken == None)
    query = filter_users_with_at_least_one_validated_offerer_validated_user_offerer(query)
    query = query.join(VenueSQLEntity).join(Offer).filter(Offer.isActive == True)
    user = query.first()

    for uo in user.UserOfferers:
        if uo.offerer.validationToken == None and uo.validationToken == None:
            for venue in uo.offerer.managedVenues:
                for offer in venue.offers:
                    if offer.isActive:
                        return {
                            "offer": get_offer_helper(offer),
                            "user": get_user_helper(user)
                        }
