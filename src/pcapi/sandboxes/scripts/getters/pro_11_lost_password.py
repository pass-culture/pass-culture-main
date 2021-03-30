from pcapi.core.users.models import Token
from pcapi.core.users.models import TokenType
from pcapi.core.users.models import User
from pcapi.models.user_offerer import UserOfferer
from pcapi.sandboxes.scripts.utils.helpers import get_pro_helper


def get_pro_validated_no_reset_password_token_user():
    query = User.query.filter((User.validationToken == None)).filter(~User.tokens.any())
    query = query.join(UserOfferer)
    user = query.first()

    return {"user": get_pro_helper(user)}


def get_pro_validated_with_reset_password_token_user():
    query = User.query.join(Token).filter(Token.type == TokenType.RESET_PASSWORD).filter(User.validationToken == None)
    query = query.join(UserOfferer)
    user = query.first()
    return {"user": get_pro_helper(user)}
