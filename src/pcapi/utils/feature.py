import os
from datetime import datetime
from functools import wraps

from pcapi.models import ApiErrors
from pcapi.models.feature import FeatureToggle
from pcapi.repository import feature_queries


def feature_required(feature_toggle: FeatureToggle):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if feature_queries.is_active(feature_toggle):
                return f(*args, **kwargs)

            errors = ApiErrors()
            errors.add_error(
                'Forbidden',
                'You don\'t have access to this page or resource'
            )
            errors.status_code = 403
            raise errors

        return wrapper

    return decorator
