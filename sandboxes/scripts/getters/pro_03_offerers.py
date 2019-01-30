from models.offerer import Offerer
from models.user import User
from repository.user_queries import filter_users_with_at_least_one_validated_offerer_validated_user_offerer, \
                                    filter_users_with_at_least_one_validated_offerer_not_validated_user_offerer, \
                                    filter_users_with_at_least_one_not_validated_offerer_validated_user_offerer
from sandboxes.scripts.utils.helpers import get_user_helper, get_offerer_helper

def get_existing_pro_validated_user_with_validated_offerer_validated_user_offerer():
    query = User.query.filter(
        (User.UserOfferers.any()) & \
        (User.validationToken == None)
    )
    query = filter_users_with_at_least_one_validated_offerer_validated_user_offerer(query)
    user = query.first()

    offerer = [
        uo.offerer for uo in user.UserOfferers
        if uo.validationToken == None \
        and uo.offerer.validationToken == None
    ][0]

    return {
        "offerer": get_offerer_helper(offerer),
        "user": get_user_helper(user)
    }

def get_existing_pro_validated_user_with_not_validated_offerer_validated_user_offerer():
    query = User.query.filter(
        (User.UserOfferers.any()) & \
        (User.validationToken == None)
    )
    query = filter_users_with_at_least_one_not_validated_offerer_validated_user_offerer(query)
    user = query.first()

    offerer = [
        uo.offerer for uo in user.UserOfferers
        if uo.validationToken == None \
        and uo.offerer.validationToken != None
    ][0]

    return {
        "offerer": get_offerer_helper(offerer),
        "user": get_user_helper(user)
    }

def get_existing_pro_validated_user_with_validated_offerer_not_validated_user_offerer():
    query = User.query.filter(
        (User.UserOfferers.any()) & \
        (User.validationToken == None)
    )
    query = filter_users_with_at_least_one_validated_offerer_not_validated_user_offerer(query)
    user = query.first()

    offerer = [
        uo.offerer for uo in user.UserOfferers
        if uo.validationToken != None \
        and uo.offerer.validationToken == None
    ][0]

    return {
        "offerer": get_offerer_helper(offerer),
        "user": get_user_helper(user)
    }
