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
@override_features(ENABLE_NATIVE_APP_RECAPTCHA=False)
def test_override_features_on_function():
    assert not feature_queries.is_active(FeatureToggle.ENABLE_NATIVE_APP_RECAPTCHA)


@pytest.mark.usefixtures("db_session")
def test_override_features_as_context_manager():
    assert feature_queries.is_active(FeatureToggle.ENABLE_NATIVE_APP_RECAPTCHA)
    with override_features(ENABLE_NATIVE_APP_RECAPTCHA=False):
        assert not feature_queries.is_active(FeatureToggle.ENABLE_NATIVE_APP_RECAPTCHA)
    assert feature_queries.is_active(FeatureToggle.ENABLE_NATIVE_APP_RECAPTCHA)


@pytest.mark.usefixtures("db_session")
class OverrideFeaturesOnClassTest:
    @override_features(ENABLE_NATIVE_APP_RECAPTCHA=False)
    def test_method_level_override(self):
        assert not feature_queries.is_active(FeatureToggle.ENABLE_NATIVE_APP_RECAPTCHA)
