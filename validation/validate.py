from models.api_errors import ResourceNotFound


def check_valid_token_for_user_validation(user_to_validate):
    if user_to_validate is None:
        errors = ResourceNotFound()
        errors.addError(
            'global',
            'Ce lien est invalide'
        )
        raise errors
