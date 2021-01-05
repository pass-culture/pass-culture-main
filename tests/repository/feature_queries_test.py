import pytest

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

    def test_is_active_returns_false_when_feature_unknown(self):
        # When / Then
        with pytest.raises(ResourceNotFoundError):
            is_active("some_random_value")
