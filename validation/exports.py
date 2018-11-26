from models.api_errors import ForbiddenError



def check_user_is_admin(user):
    if not user.isAdmin:
        api_errors = ForbiddenError()
        api_errors.addError('isAdmin', 'Vous devez être admin')
        raise api_errors
