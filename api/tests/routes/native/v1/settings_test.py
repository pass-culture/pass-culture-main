import json

from flask import current_app
import pytest

from pcapi.core.testing import override_features
from pcapi.models.feature import NATIVE_FEATURE_CACHE


pytestmark = pytest.mark.usefixtures("db_session")


@pytest.mark.usefixtures("clear_redis")
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
        APP_ENABLE_CATEGORY_FILTER_PAGE=False,
    )
    def test_get_settings_feature_combination_1(self, client):
        response = client.get("/native/v1/settings")
        assert response.status_code == 200
        assert response.json == {
            "accountCreationMinimumAge": 15,
            "appEnableAutocomplete": True,
            "appEnableCategoryFilterPage": False,
            "autoActivateDigitalBookings": True,
            "depositAmountsByAge": {"age_15": 2000, "age_16": 3000, "age_17": 3000, "age_18": 30000},
            "displayDmsRedirection": True,
            "enableFrontImageResizing": True,
            "enableNativeCulturalSurvey": True,
            "enableNativeEacIndividual": True,
            "enableNativeIdCheckVerboseDebugging": False,
            "enableNewIdentificationFlow": False,
            "enablePhoneValidation": True,
            "enableUnderageGeneralisation": True,
            "enableUserProfiling": False,
            "idCheckAddressAutocompletion": True,
            "isRecaptchaEnabled": True,
            "isWebappV2Enabled": True,
            "objectStorageUrl": "http://localhost/storage",
            "proDisableEventsQrcode": False,
            "accountUnsuspensionLimit": 60,
            "appEnableCookiesV2": False,
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
        APP_ENABLE_CATEGORY_FILTER_PAGE=True,
        APP_ENABLE_COOKIES_V2=True,
    )
    def test_get_settings_feature_combination_2(self, client):
        response = client.get("/native/v1/settings")
        assert response.status_code == 200
        assert response.json == {
            "accountCreationMinimumAge": 15,
            "appEnableAutocomplete": False,
            "appEnableCategoryFilterPage": True,
            "autoActivateDigitalBookings": True,
            "depositAmountsByAge": {"age_15": 2000, "age_16": 3000, "age_17": 3000, "age_18": 30000},
            "displayDmsRedirection": False,
            "enableFrontImageResizing": False,
            "enableNativeCulturalSurvey": False,
            "enableNativeEacIndividual": True,
            "enableNativeIdCheckVerboseDebugging": True,
            "enableNewIdentificationFlow": False,
            "enablePhoneValidation": False,
            "enableUnderageGeneralisation": True,
            "enableUserProfiling": False,
            "idCheckAddressAutocompletion": False,
            "isRecaptchaEnabled": False,
            "isWebappV2Enabled": True,
            "objectStorageUrl": "http://localhost/storage",
            "proDisableEventsQrcode": True,
            "accountUnsuspensionLimit": 60,
            "appEnableCookiesV2": True,
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
        APP_ENABLE_CATEGORY_FILTER_PAGE=True,
        APP_ENABLE_COOKIES_V2=True,
    )
    def test_cache_setup(self, client):
        redis_client = current_app.redis_client

        expected = {
            "accountCreationMinimumAge": 15,
            "appEnableAutocomplete": False,
            "appEnableCategoryFilterPage": True,
            "autoActivateDigitalBookings": True,
            "depositAmountsByAge": {"age_15": 2000, "age_16": 3000, "age_17": 3000, "age_18": 30000},
            "displayDmsRedirection": False,
            "enableFrontImageResizing": False,
            "enableNativeCulturalSurvey": False,
            "enableNativeEacIndividual": True,
            "enableNativeIdCheckVerboseDebugging": True,
            "enableNewIdentificationFlow": False,
            "enablePhoneValidation": False,
            "enableUnderageGeneralisation": True,
            "enableUserProfiling": False,
            "idCheckAddressAutocompletion": False,
            "isRecaptchaEnabled": False,
            "isWebappV2Enabled": True,
            "objectStorageUrl": "http://localhost/storage",
            "proDisableEventsQrcode": True,
            "accountUnsuspensionLimit": 60,
            "appEnableCookiesV2": True,
        }

        assert redis_client.get(NATIVE_FEATURE_CACHE) == None
        response = client.get("/native/v1/settings")
        cache = redis_client.get(NATIVE_FEATURE_CACHE)
        assert response.status_code == 200
        assert response.json == expected
        assert json.loads(cache) == expected

    def test_cache_usage(self, client):
        redis_client = current_app.redis_client

        expected = {
            "accountCreationMinimumAge": 15,
            "appEnableAutocomplete": False,
            "appEnableCategoryFilterPage": True,
            "autoActivateDigitalBookings": True,
            "depositAmountsByAge": {"age_15": 3546, "age_16": 3000, "age_17": 123456789987456321, "age_18": 666},
            "displayDmsRedirection": False,
            "enableFrontImageResizing": True,
            "enableNativeCulturalSurvey": False,
            "enableNativeEacIndividual": True,
            "enableNativeIdCheckVerboseDebugging": True,
            "enableNewIdentificationFlow": False,
            "enablePhoneValidation": False,
            "enableUnderageGeneralisation": True,
            "enableUserProfiling": False,
            "idCheckAddressAutocompletion": False,
            "isRecaptchaEnabled": False,
            "isWebappV2Enabled": True,
            "objectStorageUrl": "http://localhost/storage",
            "proDisableEventsQrcode": True,
            "accountUnsuspensionLimit": 60,
            "appEnableCookiesV2": True,
        }
        redis_client.set(NATIVE_FEATURE_CACHE, json.dumps(expected))

        response = client.get("/native/v1/settings")

        cache = redis_client.get(NATIVE_FEATURE_CACHE)
        assert response.status_code == 200
        assert response.json == expected
        assert json.loads(cache) == expected
