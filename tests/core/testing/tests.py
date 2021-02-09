import pytest

from pcapi import settings
from pcapi.core.testing import override_features
from pcapi.core.testing import override_settings
from pcapi.models.feature import FeatureToggle
from pcapi.repository import feature_queries


@override_settings(IS_RUNNING_TESTS=2)
def test_override_settings_on_function():
    assert settings.IS_RUNNING_TESTS == 2


def test_override_settings_as_context_manager():
    assert settings.IS_RUNNING_TESTS is True
    with override_settings(IS_RUNNING_TESTS=2):
        assert settings.IS_RUNNING_TESTS == 2
    assert settings.IS_RUNNING_TESTS is True


@override_settings(IS_RUNNING_TESTS=2)
class OverrideSettingsOnClassTest:
    def test_class_level_override(self):
        assert settings.IS_RUNNING_TESTS == 2

    @override_settings(IS_RUNNING_TESTS=3)
    def test_method_level_override(self):
        assert settings.IS_RUNNING_TESTS == 3


@pytest.mark.usefixtures("db_session")
@override_features(SEARCH_ALGOLIA=False)
def test_override_features_on_function():
    assert not feature_queries.is_active(FeatureToggle.SEARCH_ALGOLIA)


@pytest.mark.usefixtures("db_session")
def test_override_features_as_context_manager():
    assert feature_queries.is_active(FeatureToggle.SEARCH_ALGOLIA)
    with override_features(SEARCH_ALGOLIA=False):
        assert not feature_queries.is_active(FeatureToggle.SEARCH_ALGOLIA)
    assert feature_queries.is_active(FeatureToggle.SEARCH_ALGOLIA)


@pytest.mark.usefixtures("db_session")
class OverrideFeaturesOnClassTest:
    @override_features(SEARCH_ALGOLIA=False)
    def test_method_level_override(self):
        assert not feature_queries.is_active(FeatureToggle.SEARCH_ALGOLIA)
