import os

from models import Feature
from models.api_errors import ResourceNotFoundError
from models.feature import FeatureToggle
from utils.config import IS_PROD, IS_INTEGRATION


def feature_paid_offers_enabled() -> bool:
    return True


def find_all():
    return Feature.query.all()


def is_active(feature_toggle: FeatureToggle) -> bool:
    if type(feature_toggle) != FeatureToggle:
        raise ResourceNotFoundError
    return Feature.query \
        .filter_by(name=feature_toggle) \
        .first() \
        .isActive


def feature_send_mail_to_users_enabled() -> bool:
    return IS_PROD or IS_INTEGRATION


def feature_request_profiling_enabled() -> bool:
    return os.environ.get('PROFILE_REQUESTS', False)


def feature_write_dashboard_enabled():
    return os.environ.get('WRITE_DASHBOARD', False)


def feature_clean_seen_offers_enabled():
    return os.environ.get('CLEAN_SEEN_OFFERS') == 'true'
