import logging

from sqlalchemy.exc import IntegrityError

from pcapi.core.users.models import User
from pcapi.models.api_errors import ApiErrors
from pcapi.repository import user_queries


logger = logging.getLogger(__name__)


def validate(user: User, api_errors: ApiErrors) -> ApiErrors:
    # FIXME (dbaty, 2023-02-21): I suppose that SQLAlchemy could flush
    # changes when this SELECT query is performed, which could raise
    # an error on the UNIQUE constraint. However, I don't understand
    # why we're checking the uniqueness of the email only if the user
    # is new (which we do with `if user.id is None`).
    #
    # Update: we're not supposed to have changed the user at this
    # point, so I don't see why we would get an IntegrityError. I have
    # added a log to see if this ever happens. For the record, this
    # exception catch has been added in 60b410ccb3882bc25105cf5, which
    # does not give much clue...
    try:
        user_count = user_queries.count_users_by_email(user.email)
    except IntegrityError as exc:
        logger.info(
            "Got IntegrityError when validating user",
            extra={
                "exc": str(exc),
                "user_id": user.id,
            },
        )
        if user.id is None:
            api_errors.add_error("email", "Un compte lié à cet e-mail existe déjà")
        return api_errors

    if user.id is None and user_count > 0:
        api_errors.add_error("email", "Un compte lié à cet e-mail existe déjà")
    if user.email:
        api_errors.check_email("email", user.email)
    if user.has_admin_role and user.is_beneficiary:
        api_errors.add_error("is_beneficiary", "Admin ne peut pas être bénéficiaire")
    if user.clearTextPassword:
        api_errors.check_min_length("password", user.clearTextPassword, 8)

    return api_errors
