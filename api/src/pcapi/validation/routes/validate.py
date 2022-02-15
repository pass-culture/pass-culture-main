from pcapi.models.api_errors import ResourceNotFoundError


def check_valid_token_for_user_validation(user_to_validate):
    if user_to_validate is None:
        errors = ResourceNotFoundError()
        errors.add_error("global", "Ce lien est invalide")
        raise errors
