import pytest

from pcapi.core.testing import override_features

from tests.conftest import TestClient


pytestmark = pytest.mark.usefixtures("db_session")


class SettingsTest:
    @override_features(
        APPLY_BOOKING_LIMITS_V2=False,
        ALLOW_IDCHECK_REGISTRATION=True,
        ENABLE_NATIVE_APP_RECAPTCHA=True,
        AUTO_ACTIVATE_DIGITAL_BOOKINGS=False,
        ENABLE_NATIVE_ID_CHECK_VERSION=False,
        ENABLE_NATIVE_ID_CHECK_VERBOSE_DEBUGGING=False,
        ENABLE_ID_CHECK_RETENTION=False,
        WEBAPP_V2_ENABLED=False,
        ENABLE_PHONE_VALIDATION=True,
        WHOLE_FRANCE_OPENING=True,
        DISPLAY_DMS_REDIRECTION=True,
        USE_APP_SEARCH_ON_NATIVE_APP=True,
        ID_CHECK_ADDRESS_AUTOCOMPLETION=True,
        ENABLE_NATIVE_EAC_INDIVIDUAL=False,
    )
    def test_get_settings_feature_combination_1(self, app):
        response = TestClient(app.test_client()).get("/native/v1/settings")
        assert response.status_code == 200
        assert response.json == {
            "allowIdCheckRegistration": True,
            "autoActivateDigitalBookings": False,
            "depositAmount": 50000,
            "enableNativeIdCheckVersion": False,
            "enableNativeIdCheckVerboseDebugging": False,
            "isRecaptchaEnabled": True,
            "enablePhoneValidation": True,
            "enableIdCheckRetention": False,
            "objectStorageUrl": "http://localhost/storage",
            "wholeFranceOpening": True,
            "displayDmsRedirection": True,
            "useAppSearch": True,
            "idCheckAddressAutocompletion": True,
            "isWebappV2Enabled": False,
            "enableNativeEacIndividual": False,
        }

    @override_features(
        APPLY_BOOKING_LIMITS_V2=True,
        ALLOW_IDCHECK_REGISTRATION=False,
        ENABLE_NATIVE_APP_RECAPTCHA=False,
        ENABLE_NATIVE_ID_CHECK_VERBOSE_DEBUGGING=True,
        ENABLE_ID_CHECK_RETENTION=True,
        AUTO_ACTIVATE_DIGITAL_BOOKINGS=True,
        ENABLE_NATIVE_ID_CHECK_VERSION=True,
        WEBAPP_V2_ENABLED=True,
        ENABLE_PHONE_VALIDATION=False,
        WHOLE_FRANCE_OPENING=False,
        DISPLAY_DMS_REDIRECTION=False,
        USE_APP_SEARCH_ON_NATIVE_APP=False,
        ID_CHECK_ADDRESS_AUTOCOMPLETION=False,
        ENABLE_NATIVE_EAC_INDIVIDUAL=True,
    )
    def test_get_settings_feature_combination_2(self, app):
        response = TestClient(app.test_client()).get("/native/v1/settings")
        assert response.status_code == 200
        assert response.json == {
            "allowIdCheckRegistration": False,
            "autoActivateDigitalBookings": True,
            "depositAmount": 30000,
            "enableNativeIdCheckVersion": True,
            "enableNativeIdCheckVerboseDebugging": True,
            "isRecaptchaEnabled": False,
            "enablePhoneValidation": False,
            "enableIdCheckRetention": True,
            "objectStorageUrl": "http://localhost/storage",
            "wholeFranceOpening": False,
            "displayDmsRedirection": False,
            "useAppSearch": False,
            "idCheckAddressAutocompletion": False,
            "isWebappV2Enabled": True,
            "enableNativeEacIndividual": True,
        }
