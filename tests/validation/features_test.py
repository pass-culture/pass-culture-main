from unittest.mock import MagicMock

import pytest

from models.feature import FeatureToggle
from tests.conftest import clean_database
from tests.test_utils import create_feature
from validation.features import InconsistentFeaturesException, check_feature_enum


class CheckFeatureEnumTest:
    @clean_database
    def test_raises_inconsistent_feature_exception_if_database_and_enum_are_inconsistent(self, app):
        # Given
        find_all_features = MagicMock()
        find_all_features.return_value = []

        # When / Then
        with pytest.raises(InconsistentFeaturesException):
            check_feature_enum(find_all_features)

    @clean_database
    def test_returns_none_if_database_and_enum_are_consistent(self, app):
        # Given
        find_all_features = MagicMock()
        feature = create_feature(FeatureToggle.WEBAPP_SIGNUP, FeatureToggle.WEBAPP_SIGNUP.value, is_active=True)
        find_all_features.return_value = [feature]

        # When / Then
        assert check_feature_enum(find_all_features) is None
