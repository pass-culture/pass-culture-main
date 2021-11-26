from functools import wraps

from pcapi.models.api_errors import ApiErrors
from pcapi.models.feature import FeatureToggle


def feature_required(feature_toggle: FeatureToggle):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if feature_toggle.is_active():
                return f(*args, **kwargs)

            errors = ApiErrors()
            errors.add_error("Forbidden", "You don't have access to this page or resource")
            errors.status_code = 403
            raise errors

        return wrapper

    return decorator
