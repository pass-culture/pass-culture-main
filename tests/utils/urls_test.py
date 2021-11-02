from pcapi import settings
from pcapi.core.testing import override_features
from pcapi.utils import urls as utils


class FirebaseLinksTest:
    def test_generate_firebase_dynamic_link_without_params(self):
        url = utils.generate_firebase_dynamic_link(path="signup-confirmation", params=None)
        assert url == (
            "https://passcultureapptestauto.page.link/"
            "?link=https%3A%2F%2Fapp-native.testing.internal-passculture.app%2Fsignup-confirmation"
        )

    def test_generate_firebase_dynamic_link_with_params(self):
        url = utils.generate_firebase_dynamic_link(
            path="signup-confirmation",
            params={
                "token": "2sD3hu6DRhqhqeg4maVxJq0LGh88CkkBlrywgowuMp0",
                "expiration_timestamp": "1620905607",
                "email": "testemail@example.com",
            },
        )
        assert url == (
            "https://passcultureapptestauto.page.link/"
            "?link=https%3A%2F%2Fapp-native.testing.internal-passculture.app%2Fsignup-confirmation%3F"
            "token%3D2sD3hu6DRhqhqeg4maVxJq0LGh88CkkBlrywgowuMp0%26expiration_timestamp%3D1620905607"
            "%26email%3Dtestemail%2540example.com"
        )


class GetUrlSettingsTest:
    @override_features(WEBAPP_V2_ENABLED=False)
    def test_get_webapp_url_when_webapp_v2_enabled_is_false(self):
        assert utils.get_webapp_url() == settings.WEBAPP_URL

    @override_features(WEBAPP_V2_ENABLED=True)
    def test_get_webapp_url_when_webapp_v2_enabled_is_true(self):
        assert utils.get_webapp_url() == settings.WEBAPP_V2_URL

    @override_features(WEBAPP_V2_ENABLED=False)
    def test_get_webapp_for_native_redirection_url_when_webapp_v2_enabled_is_false(self):
        assert utils.get_webapp_for_native_redirection_url() == settings.WEBAPP_FOR_NATIVE_REDIRECTION

    @override_features(WEBAPP_V2_ENABLED=True)
    def test_get_webapp_for_native_redirection_url_when_webapp_v2_enabled_is_true(self):
        assert utils.get_webapp_for_native_redirection_url() == settings.WEBAPP_V2_URL
