from sqlalchemy.exc import IntegrityError

from pcapi.core.users.models import User
from pcapi.models import ApiErrors
from pcapi.repository import user_queries


def validate(user: User, api_errors: ApiErrors) -> ApiErrors:
    try:
        user_count = user_queries.count_users_by_email(user.email)
    except IntegrityError:
        if user.id is None:
            api_errors.add_error("email", "Un compte lié à cet e-mail existe déjà")
        return api_errors

    if user.id is None and user_count > 0:
        api_errors.add_error("email", "Un compte lié à cet e-mail existe déjà")
    if user.publicName is not None:
        api_errors.check_min_length("publicName", user.publicName, 3)
    if user.email:
        api_errors.check_email("email", user.email)
    if user.isAdmin and user.isBeneficiary:
        api_errors.add_error("isBeneficiary", "Admin ne peut pas être bénéficiaire")
    if user.clearTextPassword:
        api_errors.check_min_length("password", user.clearTextPassword, 8)

    return api_errors
