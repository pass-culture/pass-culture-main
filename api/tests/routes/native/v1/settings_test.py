import pytest

from pcapi.core.testing import override_features

from tests.conftest import TestClient


pytestmark = pytest.mark.usefixtures("db_session")


class SettingsTest:
    @override_features(
        DISPLAY_DMS_REDIRECTION=True,
        ENABLE_ID_CHECK_RETENTION=False,
        ENABLE_NATIVE_APP_RECAPTCHA=True,
        ENABLE_NATIVE_ID_CHECK_VERBOSE_DEBUGGING=False,
        ENABLE_PHONE_VALIDATION=True,
        ID_CHECK_ADDRESS_AUTOCOMPLETION=True,
        PRO_DISABLE_EVENTS_QRCODE=False,
    )
    def test_get_settings_feature_combination_1(self, app):
        response = TestClient(app.test_client()).get("/native/v1/settings")
        assert response.status_code == 200
        assert response.json == {
            "accountCreationMinimumAge": 15,
            "autoActivateDigitalBookings": True,
            "depositAmountsByAge": {"age_15": 2000, "age_16": 3000, "age_17": 3000, "age_18": 30000},
            "displayDmsRedirection": True,
            "enableIdCheckRetention": False,
            "enableNativeEacIndividual": True,
            "enableNativeIdCheckVerboseDebugging": False,
            "enablePhoneValidation": True,
            "enableUnderageGeneralisation": True,
            "idCheckAddressAutocompletion": True,
            "isRecaptchaEnabled": True,
            "isWebappV2Enabled": True,
            "objectStorageUrl": "http://localhost/storage",
            "proDisableEventsQrcode": False,
        }

    @override_features(
        DISPLAY_DMS_REDIRECTION=False,
        ENABLE_ID_CHECK_RETENTION=True,
        ENABLE_NATIVE_APP_RECAPTCHA=False,
        ENABLE_NATIVE_ID_CHECK_VERBOSE_DEBUGGING=True,
        ENABLE_PHONE_VALIDATION=False,
        ID_CHECK_ADDRESS_AUTOCOMPLETION=False,
        PRO_DISABLE_EVENTS_QRCODE=True,
    )
    def test_get_settings_feature_combination_2(self, app):
        response = TestClient(app.test_client()).get("/native/v1/settings")
        assert response.status_code == 200
        assert response.json == {
            "accountCreationMinimumAge": 15,
            "autoActivateDigitalBookings": True,
            "depositAmountsByAge": {"age_15": 2000, "age_16": 3000, "age_17": 3000, "age_18": 30000},
            "displayDmsRedirection": False,
            "enableIdCheckRetention": True,
            "enableNativeEacIndividual": True,
            "enableNativeIdCheckVerboseDebugging": True,
            "enablePhoneValidation": False,
            "enableUnderageGeneralisation": True,
            "idCheckAddressAutocompletion": False,
            "isRecaptchaEnabled": False,
            "isWebappV2Enabled": True,
            "objectStorageUrl": "http://localhost/storage",
            "proDisableEventsQrcode": True,
        }
