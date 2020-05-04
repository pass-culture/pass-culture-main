from models.offer import Offer
from models.user import User
from models.venue import Venue
from repository.user_queries import filter_users_with_at_least_one_validated_offerer_validated_user_offerer
from sandboxes.scripts.utils.helpers import get_offer_helper, get_user_helper
from utils.human_ids import humanize

def get_existing_pro_validated_user_with_at_least_one_visible_activated_offer():
    query = User.query.filter(User.validationToken == None)
    query = filter_users_with_at_least_one_validated_offerer_validated_user_offerer(query)
    query = query.join(Venue).join(Offer).filter(Offer.isActive == True)
    user = query.first()

    for userOfferer in user.UserOfferers:
        if userOfferer.offerer.validationToken is None and userOfferer.validationToken is None:
            for venue in userOfferer.offerer.managedVenues:
                for offer in venue.offers:
                    if offer.isActive:
                        return {
                            "offer": get_offer_helper(offer),
                            "mediationId": [humanize(mediation.id) for mediation in offer.mediations if mediation.isActive][0],
                            "user": get_user_helper(user)
                        }
