from pcapi.core.offerers.models import Offerer
from pcapi.core.users.models import User
from pcapi.models.user_offerer import UserOfferer
from pcapi.sandboxes.scripts.utils.helpers import get_offerer_helper
from pcapi.sandboxes.scripts.utils.helpers import get_pro_helper


def get_existing_pro_validated_user_with_first_offerer():
    query = User.query.filter(User.validationToken == None)
    query = query.join(UserOfferer)
    user = query.first()

    offerer = [uo.offerer for uo in user.UserOfferers][0]

    return {"offerer": get_offerer_helper(offerer), "user": get_pro_helper(user)}


def get_existing_pro_validated_user_with_offerer_with_no_iban():
    query = User.query.join(UserOfferer).join(Offerer).filter(User.UserOfferers.any(Offerer.bankInformation == None))
    query = query.filter(User.validationToken == None)
    user = query.first()

    offerer = [uo.offerer for uo in user.UserOfferers if uo.offerer.iban == None][0]

    return {"offerer": get_offerer_helper(offerer), "user": get_pro_helper(user)}
