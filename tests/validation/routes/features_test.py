import pytest

from pcapi.models.feature import Feature
from pcapi.repository import repository
from pcapi.validation.routes.features import InconsistentFeaturesException
from pcapi.validation.routes.features import check_feature_consistency


class CheckFeatureConsistencyTest:
    @pytest.mark.usefixtures("db_session")
    def test_raises_if_inconsistency(self):
        feature = Feature(name="FeatureToggle.PANIC_MODE", description="Activate panic mode")
        repository.save(feature)

        with pytest.raises(InconsistentFeaturesException):
            check_feature_consistency()

    @pytest.mark.usefixtures("db_session")
    def test_returns_none_if_consistent(self):
        assert check_feature_consistency() is None
