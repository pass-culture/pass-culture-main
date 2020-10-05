import pytest

from models.api_errors import ResourceNotFoundError
from models.feature import FeatureToggle, Feature
from repository import repository
from repository.feature_queries import is_active
import pytest


class FeatureToggleTest:
    @pytest.mark.usefixtures("db_session")
    def test_is_active_returns_true_when_feature_is_active(self, app):
        # Given
        feature = Feature.query.filter_by(name=FeatureToggle.WEBAPP_SIGNUP).first()
        feature.isActive = True
        repository.save(feature)

        # When / Then
        assert is_active(FeatureToggle.WEBAPP_SIGNUP)

    @pytest.mark.usefixtures("db_session")
    def test_is_active_returns_false_when_feature_is_inactive(self, app):
        # Given
        feature = Feature.query.filter_by(name=FeatureToggle.WEBAPP_SIGNUP).first()
        feature.isActive = False
        repository.save(feature)
        # When / Then
        assert not is_active(FeatureToggle.WEBAPP_SIGNUP)

    @pytest.mark.usefixtures("db_session")
    def test_is_active_returns_false_when_feature_unknown(self, app):
        # When / Then
        with pytest.raises(ResourceNotFoundError):
            is_active('some_random_value')
