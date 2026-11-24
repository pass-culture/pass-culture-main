import pytest

from pcapi.core.offers.constants import get_legacy_screening_features


class GetLegacyScreeningFeaturesTest:
    @pytest.mark.parametrize(
        "features, expected",
        [
            ([], []),
            (["VF", "VO"], ["VF", "VO"]),
            (["VF", "SCREEN_X"], ["VF"]),
            (["SCREEN_X", "GRETA"], []),
        ],
    )
    def test_keeps_only_legacy_features(self, features, expected):
        assert get_legacy_screening_features(features) == expected
