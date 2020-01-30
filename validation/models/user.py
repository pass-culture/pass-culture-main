from sqlalchemy.exc import IntegrityError

from models import ApiErrors
from models.db import Model
from repository import user_queries


def get_user_errors(model: Model, api_errors: ApiErrors) -> ApiErrors:
    user_count = 0
    try:
        user_count = user_queries.count_users_by_email(model.email)
    except IntegrityError:
        if model.id is None:
            api_errors.add_error('email', 'Un compte lié à cet e-mail existe déjà')

    if model.id is None and user_count > 0:
        api_errors.add_error('email', 'Un compte lié à cet e-mail existe déjà')
    if model.publicName:
        api_errors.check_min_length('publicName', model.publicName, 3)
    if model.email:
        api_errors.check_email('email', model.email)
    if model.isAdmin and model.canBookFreeOffers:
        api_errors.add_error('canBookFreeOffers', 'Admin ne peut pas réserver')
    if model.clearTextPassword:
        api_errors.check_min_length('password', model.clearTextPassword, 8)

    return api_errors
