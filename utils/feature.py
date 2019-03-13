from models.feature import FeatureToggle
from repository import feature_queries


def feature_required(feature_toggle: FeatureToggle):
    def decorator(f):
        def wrapper(*args, **kwargs):
            if feature_queries.is_active(feature_toggle):
                return f(*args, **kwargs)

            return '', 404
        return wrapper
    return decorator