import flask
import pytest

from pcapi.core.testing import assert_num_queries
from pcapi.models.api_errors import ResourceNotFoundError
from pcapi.models.feature import Feature
from pcapi.models.feature import FeatureToggle
from pcapi.repository import repository
from pcapi.repository.feature_queries import is_active


@pytest.mark.usefixtures("db_session")
class FeatureToggleTest:
    def test_is_active_returns_true_when_feature_is_active(self):
        # Given
        feature = Feature.query.filter_by(name=FeatureToggle.WEBAPP_SIGNUP.name).first()
        feature.isActive = True
        repository.save(feature)

        # When / Then
        assert is_active(FeatureToggle.WEBAPP_SIGNUP)

    def test_is_active_returns_false_when_feature_is_inactive(self):
        # Given
        feature = Feature.query.filter_by(name=FeatureToggle.WEBAPP_SIGNUP.name).first()
        feature.isActive = False
        repository.save(feature)
        # When / Then
        assert not is_active(FeatureToggle.WEBAPP_SIGNUP)

    def test_is_active_raises_exception_when_feature_is_unknown(self):
        # When / Then
        with pytest.raises(ResourceNotFoundError):
            is_active("some_random_value")

    def test_is_active_query_count_inside_request_context(self):
        feature = Feature.query.filter_by(name=FeatureToggle.WEBAPP_SIGNUP.name).first()
        feature.isActive = True
        repository.save(feature)

        # we should only have a single DB query here thanks to the cache
        with assert_num_queries(1):
            is_active(FeatureToggle.WEBAPP_SIGNUP)
            is_active(FeatureToggle.WEBAPP_SIGNUP)
            is_active(FeatureToggle.WEBAPP_SIGNUP)

    def test_is_active_query_count_outside_request_context(self, app):
        feature = Feature.query.filter_by(name=FeatureToggle.WEBAPP_SIGNUP.name).first()
        feature.isActive = True
        repository.save(feature)
        context = flask._request_ctx_stack.pop()

        # we don't cache yet outside the scope of a request so it'll be 3 DB queries
        try:
            with assert_num_queries(3):
                is_active(FeatureToggle.WEBAPP_SIGNUP)
                is_active(FeatureToggle.WEBAPP_SIGNUP)
                is_active(FeatureToggle.WEBAPP_SIGNUP)
        finally:
            flask._request_ctx_stack.push(context)
