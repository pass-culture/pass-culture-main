import pytest

from models import PcObject
from models.api_errors import ResourceNotFound
from models.feature import FeatureToggle, Feature
from repository.feature_queries import is_active
from tests.conftest import clean_database


class FeatureToggleTest:
    @clean_database
    def test_is_active_returns_true_when_feature_is_active(self, app):
        # Given
        feature = Feature.query.filter_by(name=FeatureToggle.WEBAPP_SIGNUP).first()
        feature.isActive = True
        PcObject.save(feature)

        # When / Then
        assert is_active(FeatureToggle.WEBAPP_SIGNUP)

    @clean_database
    def test_is_active_returns_false_when_feature_is_inactive(self, app):
        # Given
        feature = Feature.query.filter_by(name=FeatureToggle.WEBAPP_SIGNUP).first()
        feature.isActive = False
        PcObject.save(feature)
        # When / Then
        assert not is_active(FeatureToggle.WEBAPP_SIGNUP)

    @clean_database
    def test_is_active_returns_false_when_feature_unknown(self, app):
        # When / Then
        with pytest.raises(ResourceNotFound):
            is_active('some_random_value')
