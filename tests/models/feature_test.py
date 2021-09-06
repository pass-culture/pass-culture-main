import flask
import pytest

from pcapi.core.testing import assert_num_queries
from pcapi.models.feature import FEATURES_DISABLED_BY_DEFAULT
from pcapi.models.feature import Feature
from pcapi.models.feature import FeatureToggle
from pcapi.repository import repository


@pytest.mark.usefixtures("db_session")
class FeatureToggleTest:
    def test_is_active_returns_true_when_feature_is_active(self):
        # Given
        feature = Feature.query.filter_by(name=FeatureToggle.WEBAPP_SIGNUP.name).first()
        feature.isActive = True
        repository.save(feature)

        # When / Then
        assert FeatureToggle.WEBAPP_SIGNUP.is_active()

    def test_is_active_returns_false_when_feature_is_inactive(self):
        # Given
        feature = Feature.query.filter_by(name=FeatureToggle.WEBAPP_SIGNUP.name).first()
        feature.isActive = False
        repository.save(feature)
        # When / Then
        assert not FeatureToggle.WEBAPP_SIGNUP.is_active()

    def test_is_active_query_count_inside_request_context(self):
        feature = Feature.query.filter_by(name=FeatureToggle.WEBAPP_SIGNUP.name).first()
        feature.isActive = True
        repository.save(feature)

        with assert_num_queries(1):
            FeatureToggle.WEBAPP_SIGNUP.is_active()
            FeatureToggle.WEBAPP_SIGNUP.is_active()
            FeatureToggle.WEBAPP_SIGNUP.is_active()

    def test_is_active_query_count_outside_request_context(self, app):
        feature = Feature.query.filter_by(name=FeatureToggle.WEBAPP_SIGNUP.name).first()
        feature.isActive = True
        repository.save(feature)
        context = flask._request_ctx_stack.pop()

        # we don't cache yet outside the scope of a request so it'll be 3 DB queries
        try:
            with assert_num_queries(3):
                FeatureToggle.WEBAPP_SIGNUP.is_active()
                FeatureToggle.WEBAPP_SIGNUP.is_active()
                FeatureToggle.WEBAPP_SIGNUP.is_active()

        finally:
            flask._request_ctx_stack.push(context)


@pytest.mark.usefixtures("db_session")
class FeatureTest:
    def test_features_installation(self):
        # assert all defined feature flags are present in the database with the right initial value
        for flag in list(FeatureToggle):
            assert Feature.query.filter_by(name=flag.name).first().isActive == (
                flag not in FEATURES_DISABLED_BY_DEFAULT
            )
