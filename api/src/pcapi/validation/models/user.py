import logging

from pcapi.core.users.models import User
import pcapi.core.users.repository as users_repository
from pcapi.models.api_errors import ApiErrors


logger = logging.getLogger(__name__)


def validate(user: User, api_errors: ApiErrors) -> ApiErrors:
    user_with_this_email = users_repository.find_user_by_email(user.email)

    if user_with_this_email and user_with_this_email.id != user.id:
        api_errors.add_error("email", "Un compte lié à cet email existe déjà")
    if user.email:
        api_errors.check_email("email", user.email)
    if user.has_admin_role and user.is_beneficiary:
        api_errors.add_error("is_beneficiary", "Admin ne peut pas être bénéficiaire")
    if user.clearTextPassword:
        api_errors.check_min_length("password", user.clearTextPassword, 8)

    return api_errors
