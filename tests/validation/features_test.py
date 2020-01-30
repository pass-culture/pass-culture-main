from unittest.mock import MagicMock

import pytest

from models.feature import FeatureToggle, Feature
from tests.conftest import clean_database
from validation.routes.features import InconsistentFeaturesException, check_feature_consistency


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
        features = []
        for feature_toggle in FeatureToggle:
            feature = Feature()
            feature.populate_from_dict({'name': feature_toggle})
            features.append(feature)
        find_all_features.return_value = features

        # When / Then
        assert check_feature_consistency(find_all_features) is None
