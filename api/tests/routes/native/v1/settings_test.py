import pytest

from pcapi.core.testing import override_features

from tests.conftest import TestClient


pytestmark = pytest.mark.usefixtures("db_session")


class SettingsTest:
    @override_features(
        ALLOW_IDCHECK_REGISTRATION=True,
        AUTO_ACTIVATE_DIGITAL_BOOKINGS=False,
        DISPLAY_DMS_REDIRECTION=True,
        ENABLE_ID_CHECK_RETENTION=False,
        ENABLE_NATIVE_APP_RECAPTCHA=True,
        ENABLE_NATIVE_EAC_INDIVIDUAL=False,
        ENABLE_NATIVE_ID_CHECK_VERBOSE_DEBUGGING=False,
        ENABLE_PHONE_VALIDATION=True,
        ID_CHECK_ADDRESS_AUTOCOMPLETION=True,
        WEBAPP_V2_ENABLED=False,
    )
    def test_get_settings_feature_combination_1(self, app):
        response = TestClient(app.test_client()).get("/native/v1/settings")
        assert response.status_code == 200
        assert response.json == {
            "accountCreationMinimumAge": 15,
            "allowIdCheckRegistration": True,
            "autoActivateDigitalBookings": False,
            "depositAmount": 30000,
            "depositAmountsByAge": {"age_15": 2000, "age_16": 3000, "age_17": 3000, "age_18": 30000},
            "displayDmsRedirection": True,
            "enableIdCheckRetention": False,
            "enableNativeEacIndividual": False,
            "enableNativeIdCheckVerboseDebugging": False,
            "enablePhoneValidation": True,
            "enableUnderageGeneralisation": False,
            "idCheckAddressAutocompletion": True,
            "isRecaptchaEnabled": True,
            "isWebappV2Enabled": False,
            "objectStorageUrl": "http://localhost/storage",
        }

    @override_features(
        ALLOW_IDCHECK_REGISTRATION=False,
        ENABLE_NATIVE_APP_RECAPTCHA=False,
        ENABLE_NATIVE_ID_CHECK_VERBOSE_DEBUGGING=True,
        ENABLE_ID_CHECK_RETENTION=True,
        AUTO_ACTIVATE_DIGITAL_BOOKINGS=True,
        WEBAPP_V2_ENABLED=True,
        ENABLE_PHONE_VALIDATION=False,
        DISPLAY_DMS_REDIRECTION=False,
        ID_CHECK_ADDRESS_AUTOCOMPLETION=False,
        ENABLE_NATIVE_EAC_INDIVIDUAL=True,
    )
    def test_get_settings_feature_combination_2(self, app):
        response = TestClient(app.test_client()).get("/native/v1/settings")
        assert response.status_code == 200
        assert response.json == {
            "accountCreationMinimumAge": 15,
            "allowIdCheckRegistration": False,
            "autoActivateDigitalBookings": True,
            "depositAmount": 30000,
            "depositAmountsByAge": {"age_15": 2000, "age_16": 3000, "age_17": 3000, "age_18": 30000},
            "displayDmsRedirection": False,
            "enableIdCheckRetention": True,
            "enableNativeEacIndividual": True,
            "enableNativeIdCheckVerboseDebugging": True,
            "enablePhoneValidation": False,
            "enableUnderageGeneralisation": False,
            "idCheckAddressAutocompletion": False,
            "isRecaptchaEnabled": False,
            "isWebappV2Enabled": True,
            "objectStorageUrl": "http://localhost/storage",
        }
