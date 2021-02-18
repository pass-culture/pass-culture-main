from flask import has_request_context
from flask import request

from pcapi.models.api_errors import ResourceNotFoundError
from pcapi.models.feature import Feature
from pcapi.models.feature import FeatureToggle


def find_all():
    return Feature.query.all()


def is_active(feature_toggle: FeatureToggle) -> bool:
    if not isinstance(feature_toggle, FeatureToggle):
        raise ResourceNotFoundError

    if has_request_context():
        if not hasattr(request, "_cached_features"):
            setattr(request, "_cached_features", {})

        cached_value = request._cached_features.get(feature_toggle.name)
        if cached_value is not None:
            return cached_value

    value = Feature.query.filter_by(name=feature_toggle.name).first().isActive

    if has_request_context():
        request._cached_features[feature_toggle.name] = value

    return value
