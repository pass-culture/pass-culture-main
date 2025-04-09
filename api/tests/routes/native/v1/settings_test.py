import pytest

from pcapi.core.testing import assert_num_queries
from pcapi.utils.postal_code import INELIGIBLE_POSTAL_CODES


pytestmark = pytest.mark.usefixtures("db_session")


class SettingsTest:
    @pytest.mark.features(
        DISPLAY_DMS_REDIRECTION=True,
        ENABLE_FRONT_IMAGE_RESIZING=True,
        ENABLE_NATIVE_APP_RECAPTCHA=True,
        ENABLE_NATIVE_CULTURAL_SURVEY=True,
        ENABLE_PHONE_VALIDATION=True,
        ID_CHECK_ADDRESS_AUTOCOMPLETION=True,
        APP_ENABLE_AUTOCOMPLETE=True,
    )
    def test_get_settings_feature_combination_1(self, client):
        with assert_num_queries(1):  # feature
            response = client.get("/native/v1/settings")
            assert response.status_code == 200

        assert response.json == {
            "accountCreationMinimumAge": 15,
            "appEnableAutocomplete": True,
            "depositAmountsByAge": {"age_15": 0, "age_16": 0, "age_17": 5000, "age_18": 15000},
            "displayDmsRedirection": True,
            "enableFrontImageResizing": True,
            "enableNativeCulturalSurvey": True,
            "enablePhoneValidation": True,
            "idCheckAddressAutocompletion": True,
            "isRecaptchaEnabled": True,
            "objectStorageUrl": "http://localhost/storage",
            "accountUnsuspensionLimit": 60,
            "rates": {"pacificFrancToEuro": 0.00838},
            "wipEnableCreditV3": True,
            "ineligiblePostalCodes": INELIGIBLE_POSTAL_CODES,
        }

    @pytest.mark.features(
        DISPLAY_DMS_REDIRECTION=False,
        ENABLE_FRONT_IMAGE_RESIZING=False,
        ENABLE_NATIVE_APP_RECAPTCHA=False,
        ENABLE_NATIVE_CULTURAL_SURVEY=False,
        ENABLE_PHONE_VALIDATION=False,
        ID_CHECK_ADDRESS_AUTOCOMPLETION=False,
        APP_ENABLE_AUTOCOMPLETE=False,
    )
    def test_get_settings_feature_combination_2(self, client):
        with assert_num_queries(1):  # feature
            response = client.get("/native/v1/settings")
            assert response.status_code == 200

        assert response.json == {
            "accountCreationMinimumAge": 15,
            "appEnableAutocomplete": False,
            "depositAmountsByAge": {"age_15": 0, "age_16": 0, "age_17": 5000, "age_18": 15000},
            "displayDmsRedirection": False,
            "enableFrontImageResizing": False,
            "enableNativeCulturalSurvey": False,
            "enablePhoneValidation": False,
            "idCheckAddressAutocompletion": False,
            "isRecaptchaEnabled": False,
            "objectStorageUrl": "http://localhost/storage",
            "accountUnsuspensionLimit": 60,
            "rates": {"pacificFrancToEuro": 0.00838},
            "wipEnableCreditV3": True,
            "ineligiblePostalCodes": INELIGIBLE_POSTAL_CODES,
        }
