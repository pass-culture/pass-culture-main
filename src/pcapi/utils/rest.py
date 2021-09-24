from functools import wraps

from flask import request

from pcapi.core.users.models import User
from pcapi.models.api_errors import ApiErrors
from pcapi.utils.human_ids import dehumanize


def expect_json_data(f):
    @wraps(f)
    def wrapper(*args, **kwds):
        if request.json is None:
            return "JSON data expected", 400
        return f(*args, **kwds)

    return wrapper


def check_user_has_access_to_offerer(user: User, offerer_id: int):
    if not user.has_access(offerer_id):
        errors = ApiErrors()
        errors.add_error("global", "Vous n'avez pas les droits d'accès suffisant pour accéder à cette information.")
        errors.status_code = 403
        raise errors


def load_or_404(obj_class, human_id):
    return obj_class.query.filter_by(id=dehumanize(human_id)).first_or_404()


def load_or_raise_error(obj_class, human_id):
    data = obj_class.query.filter_by(id=dehumanize(human_id)).one_or_none()
    if data is None:
        errors = ApiErrors()
        errors.add_error("global", "Aucun objet ne correspond à cet identifiant dans notre base de données")
        errors.status_code = 400
        raise errors

    return data
