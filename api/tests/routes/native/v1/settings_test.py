import pytest

from pcapi.core.testing import override_features

from tests.conftest import TestClient


class SettingsTest:
    @override_features(
        DISPLAY_DMS_REDIRECTION=True,
        ENABLE_FRONT_IMAGE_RESIZING=True,
        ENABLE_NATIVE_APP_RECAPTCHA=True,
        ENABLE_NATIVE_CULTURAL_SURVEY=True,
        ENABLE_NATIVE_ID_CHECK_VERBOSE_DEBUGGING=False,
        ENABLE_PHONE_VALIDATION=True,
        ID_CHECK_ADDRESS_AUTOCOMPLETION=True,
        PRO_DISABLE_EVENTS_QRCODE=False,
        APP_ENABLE_AUTOCOMPLETE=True,
    )
    def test_get_settings_feature_combination_1(self, app):
        response = TestClient(app.test_client()).get("/native/v1/settings")
        assert response.status_code == 200
        assert response.json == {
            "accountCreationMinimumAge": 15,
            "appEnableAutocomplete": True,
            "depositAmountsByAge": {"age_15": 2000, "age_16": 3000, "age_17": 3000, "age_18": 30000},
            "displayDmsRedirection": True,
            "enableFrontImageResizing": True,
            "enableNativeCulturalSurvey": True,
            "enableNativeIdCheckVerboseDebugging": False,
            "enablePhoneValidation": True,
            "idCheckAddressAutocompletion": True,
            "isRecaptchaEnabled": True,
            "objectStorageUrl": "http://localhost/storage",
            "proDisableEventsQrcode": False,
            "accountUnsuspensionLimit": 60,
        }

    @override_features(
        DISPLAY_DMS_REDIRECTION=False,
        ENABLE_FRONT_IMAGE_RESIZING=False,
        ENABLE_NATIVE_APP_RECAPTCHA=False,
        ENABLE_NATIVE_CULTURAL_SURVEY=False,
        ENABLE_NATIVE_ID_CHECK_VERBOSE_DEBUGGING=True,
        ENABLE_PHONE_VALIDATION=False,
        ID_CHECK_ADDRESS_AUTOCOMPLETION=False,
        PRO_DISABLE_EVENTS_QRCODE=True,
        APP_ENABLE_AUTOCOMPLETE=False,
    )
    def test_get_settings_feature_combination_2(self, app):
        response = TestClient(app.test_client()).get("/native/v1/settings")
        assert response.status_code == 200
        assert response.json == {
            "accountCreationMinimumAge": 15,
            "appEnableAutocomplete": False,
            "depositAmountsByAge": {"age_15": 2000, "age_16": 3000, "age_17": 3000, "age_18": 30000},
            "displayDmsRedirection": False,
            "enableFrontImageResizing": False,
            "enableNativeCulturalSurvey": False,
            "enableNativeIdCheckVerboseDebugging": True,
            "enablePhoneValidation": False,
            "idCheckAddressAutocompletion": False,
            "isRecaptchaEnabled": False,
            "objectStorageUrl": "http://localhost/storage",
            "proDisableEventsQrcode": True,
            "accountUnsuspensionLimit": 60,
        }
