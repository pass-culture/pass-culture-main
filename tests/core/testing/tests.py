from pcapi import settings
from pcapi.core.testing import override_settings


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
