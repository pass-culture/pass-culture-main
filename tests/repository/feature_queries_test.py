from models.feature import FeatureToggle
from repository.feature_queries import is_active, activate, deactivate
from tests.conftest import clean_database


class FeatureToggleTest:
    @clean_database
    def test_is_active_returns_true_when_feature_is_active(self, app):
        # Given
        activate(FeatureToggle.WEBAPP_SIGNUP)

        # When / Then
        assert is_active(FeatureToggle.WEBAPP_SIGNUP)

    @clean_database
    def test_is_active_returns_false_when_feature_is_inactive(self, app):
        # Given
        deactivate(FeatureToggle.WEBAPP_SIGNUP)

        # When / Then
        assert not is_active(FeatureToggle.WEBAPP_SIGNUP)
