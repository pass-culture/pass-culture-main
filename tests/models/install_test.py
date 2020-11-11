import pytest

from pcapi.models import Feature
from pcapi.models.feature import FeatureToggle
from pcapi.models.install import install_features


class InstallFeaturesTest:
    @pytest.mark.usefixtures("db_session")
    def test_creates_active_features_in_database(self, app):
        # Given
        Feature.query.delete()

        # When
        install_features()

        # Then
        for feature_toggle in FeatureToggle:
            feature = Feature.query.filter_by(name=feature_toggle).one()
            assert feature.description == feature_toggle.value
            assert feature.isActive
