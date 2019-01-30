from models.user import User
from repository.user_queries import filter_users_with_at_least_one_activated_offer
from sandboxes.scripts.utils.helpers import get_offer_helper, get_user_helper

def get_existing_pro_validated_user_with_at_least_one_activated_offer():
    query = User.query.filter(User.UserOfferers.any())
    query = query.filter(User.validationToken == None)
    query = filter_users_with_at_least_one_activated_offer(query)
    user = query.first()

    for uo in user.UserOfferers:
        for venue in uo.offerer.managedVenues:
            for offer in venue.offers:
                if offer.isActive:
                    return {
                        "offer": get_offer_helper(offer),
                        "user": get_user_helper(user)
                    }
