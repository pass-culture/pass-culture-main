from pcapi.core.users.models import Token
from pcapi.core.users.models import TokenType
from pcapi.core.users.models import User
from pcapi.repository.user_queries import keep_only_webapp_users
from pcapi.sandboxes.scripts.utils.helpers import get_beneficiary_helper


def get_existing_webapp_not_validated_user():
    query = keep_only_webapp_users(User.query)
    query = query.join(Token).filter(Token.type == TokenType.RESET_PASSWORD)
    user = query.first()

    return {"user": get_beneficiary_helper(user)}


def get_existing_webapp_validated_user():
    query = keep_only_webapp_users(User.query)
    query = query.filter(~User.tokens.any())
    user = query.first()

    return {"user": get_beneficiary_helper(user)}
