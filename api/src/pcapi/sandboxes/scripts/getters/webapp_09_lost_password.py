from pcapi.core.users.models import Token
from pcapi.core.users.models import TokenType
from pcapi.core.users.models import User
from pcapi.repository.user_queries import keep_only_webapp_users
from pcapi.sandboxes.scripts.utils.helpers import get_beneficiary_helper


def get_webapp_user_with_not_validated_password() -> dict:
    query = keep_only_webapp_users(User.query)
    query = query.join(Token).filter(Token.type == TokenType.RESET_PASSWORD, Token.isUsed.is_(False))
    user = query.first()

    return {"user": get_beneficiary_helper(user)}
