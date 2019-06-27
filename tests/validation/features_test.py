from unittest.mock import MagicMock

import pytest

from models.feature import FeatureToggle, Feature
from tests.conftest import clean_database
from validation.features import InconsistentFeaturesException, check_feature_consistency


class CheckFeatureConsistencyTest:
    @clean_database
    def test_raises_inconsistent_feature_exception_if_database_and_enum_are_inconsistent(self, app):
        # Given
        find_all_features = MagicMock()
        find_all_features.return_value = []

        # When / Then
        with pytest.raises(InconsistentFeaturesException):
            check_feature_consistency(find_all_features)

    @clean_database
    def test_returns_none_if_database_and_enum_are_consistent(self, app):
        # Given
        find_all_features = MagicMock()
        feature = Feature(name=FeatureToggle.WEBAPP_SIGNUP)
        find_all_features.return_value = [feature]

        # When / Then
        assert check_feature_consistency(find_all_features) is None
