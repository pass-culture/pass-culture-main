from models.offerer import Offerer
from models.user import User
from models.user_offerer import UserOfferer
from sandboxes.scripts.utils.helpers import get_user_helper, get_offerer_helper

def get_existing_pro_user_with_offerer():
    query = User.query.filter(User.UserOfferers.any())
    user = query.first()

    offerer = [
        uo.offerer for uo in user.UserOfferers
    ][0]

    return {
        "offerer": get_offerer_helper(offerer),
        "user": get_user_helper(user)
    }

def get_existing_pro_not_validated_user_with_real_offerer():
    query = User.query.filter(
        (User.validationToken != None)
    )
    query = query.join(UserOfferer) \
                 .join(Offerer) \
                 .filter(~Offerer.siren.startswith('222'))
    user = query.first()

    offerer = [
        uo.offerer for uo in user.UserOfferers
        if not uo.offerer.siren.startswith('222')
    ][0]

    return {
        "offerer": get_offerer_helper(offerer),
        "user": get_user_helper(user)
    }
