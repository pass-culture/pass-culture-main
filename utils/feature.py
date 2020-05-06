import os
from datetime import datetime
from functools import wraps

from models import ApiErrors
from models.feature import FeatureToggle
from repository import feature_queries


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


def get_feature_end_of_quarantine_date() -> datetime:
    end_of_quarantine = os.environ.get('END_OF_QUARANTINE_DATE', '2020-04-25')
    if not end_of_quarantine:
        end_of_quarantine = '2020-04-25'
    return datetime.strptime(end_of_quarantine, '%Y-%m-%d')
