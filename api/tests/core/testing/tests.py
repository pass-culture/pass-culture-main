import pathlib
import tempfile

import pytest

from pcapi import settings
from pcapi.core.testing import clean_temporary_files
from pcapi.core.testing import override_features
from pcapi.core.testing import override_settings
from pcapi.models.feature import FeatureToggle


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


@override_features(ENABLE_NATIVE_APP_RECAPTCHA=False)
def test_override_features_on_function():
    assert not FeatureToggle.ENABLE_NATIVE_APP_RECAPTCHA.is_active()


def test_override_features_as_context_manager():
    assert FeatureToggle.ENABLE_NATIVE_APP_RECAPTCHA.is_active()
    with override_features(ENABLE_NATIVE_APP_RECAPTCHA=False):
        assert not FeatureToggle.ENABLE_NATIVE_APP_RECAPTCHA.is_active()
    assert FeatureToggle.ENABLE_NATIVE_APP_RECAPTCHA.is_active()


class OverrideFeaturesOnClassTest:
    @override_features(ENABLE_NATIVE_APP_RECAPTCHA=False)
    def test_method_level_override(self):
        assert not FeatureToggle.ENABLE_NATIVE_APP_RECAPTCHA.is_active()


def test_clean_temporary_files():
    created = []

    @clean_temporary_files
    def func():
        file1 = pathlib.Path(tempfile.mkstemp()[1])
        created.append(file1)
        dir1 = pathlib.Path(tempfile.mkdtemp())
        created.append(dir1)
        file2 = dir1 / "marker.txt"
        file2.touch()  # make `dir1` non empty
        created.append(file2)
        # Make sure that files are cleaned even if there is an error.
        raise ValueError()

    with pytest.raises(ValueError):
        func()

    assert len(created) == 3
    for path in created:
        assert not path.exists()
