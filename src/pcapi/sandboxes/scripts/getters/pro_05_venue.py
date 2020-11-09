from pcapi.models.user_sql_entity import UserSQLEntity
from pcapi.repository.offerer_queries import keep_offerers_with_at_least_one_physical_venue
from pcapi.repository.offerer_queries import keep_offerers_with_no_physical_venue
from pcapi.repository.user_queries import filter_users_with_at_least_one_validated_offerer_validated_user_offerer
from pcapi.sandboxes.scripts.utils.helpers import get_offerer_helper
from pcapi.sandboxes.scripts.utils.helpers import get_pro_helper
from pcapi.sandboxes.scripts.utils.helpers import get_venue_helper


def get_existing_pro_validated_user_with_validated_offerer_validated_user_offerer_no_physical_venue():
    query = UserSQLEntity.query.filter(UserSQLEntity.validationToken == None)
    query = filter_users_with_at_least_one_validated_offerer_validated_user_offerer(query)
    query = keep_offerers_with_no_physical_venue(query)
    user = query.first()

    offerer = [
        uo.offerer for uo in user.UserOfferers
        if uo.offerer.validationToken == None \
        and uo.validationToken == None \
        and all([v.isVirtual for v in uo.offerer.managedVenues])
    ][0]

    return {
        "offerer": get_offerer_helper(offerer),
        "user": get_pro_helper(user)
    }

def get_existing_pro_validated_user_with_validated_offerer_validated_user_offerer_with_at_least_one_physical_venue():
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
