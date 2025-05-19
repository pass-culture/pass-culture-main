import pytest

import pcapi.core.bookings.models as bookings_models
from pcapi import settings as pcapi_settings
from pcapi.core.testing import assert_no_duplicated_queries
from pcapi.models import db
from pcapi.models.feature import FeatureToggle


class AssertNoDuplicatedQueriesTest:
    def _run_dummy_query(self):
        # We cast to list to force query execution
        list(db.session.query(bookings_models.Booking).all())

    def test_passes_when_no_queries(self):
        with assert_no_duplicated_queries():
            pass

    def test_passes_when_no_duplicated_queries(self):
        with assert_no_duplicated_queries():
            self._run_dummy_query()

    def test_fails_when_duplicated_queries(self):
        with pytest.raises(AssertionError):
            with assert_no_duplicated_queries():
                self._run_dummy_query()
                self._run_dummy_query()


@pytest.mark.settings(IS_RUNNING_TESTS=2)
def test_override_settings_on_function():
    assert pcapi_settings.IS_RUNNING_TESTS == 2


def test_override_settings_as_context_manager(settings):
    assert pcapi_settings.IS_RUNNING_TESTS is True
    settings.IS_RUNNING_TESTS = 2
    assert pcapi_settings.IS_RUNNING_TESTS == 2
    settings.IS_RUNNING_TESTS = True
    assert pcapi_settings.IS_RUNNING_TESTS is True


@pytest.mark.settings(IS_RUNNING_TESTS=2)
class OverrideSettingsOnClassTest:
    def test_class_level_override(self):
        assert pcapi_settings.IS_RUNNING_TESTS == 2

    @pytest.mark.settings(IS_RUNNING_TESTS=3)
    def test_method_level_override(self):
        assert pcapi_settings.IS_RUNNING_TESTS == 3


@pytest.mark.features(ENABLE_NATIVE_APP_RECAPTCHA=False)
def test_override_features_on_function():
    assert not FeatureToggle.ENABLE_NATIVE_APP_RECAPTCHA.is_active()


def test_override_features_as_context_manager(features):
    assert FeatureToggle.ENABLE_NATIVE_APP_RECAPTCHA.is_active()
    features.ENABLE_NATIVE_APP_RECAPTCHA = False
    assert not FeatureToggle.ENABLE_NATIVE_APP_RECAPTCHA.is_active()
    features.ENABLE_NATIVE_APP_RECAPTCHA = True
    assert FeatureToggle.ENABLE_NATIVE_APP_RECAPTCHA.is_active()


@pytest.mark.features(ENABLE_NATIVE_APP_RECAPTCHA=False)
class OverrideFeaturesOnClassTest:
    def test_method_level_override(self):
        assert not FeatureToggle.ENABLE_NATIVE_APP_RECAPTCHA.is_active()
