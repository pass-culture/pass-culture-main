import pytest

import pcapi.core.offers.factories as offers_factories
from pcapi.utils import urls


class FirebaseLinksTest:
    @pytest.mark.features(USE_UNIVERSAL_LINKS=True)
    def test_generate_universal_link_without_params(self):
        url = urls.generate_app_link(path="signup-confirmation", params=None)
        assert url == "https://webapp-v2.example.com/signup-confirmation"

    @pytest.mark.features(USE_UNIVERSAL_LINKS=True)
    def test_generate_universal_link_with_params(self):
        url = urls.generate_app_link(
            path="signup-confirmation",
            params={
                "token": "2sD3hu6DRhqhqeg4maVxJq0LGh88CkkBlrywgowuMp0",
                "expiration_timestamp": "1620905607",
                "email": "testemail@example.com",
            },
        )
        assert (
            url
            == "https://webapp-v2.example.com/signup-confirmation?token=2sD3hu6DRhqhqeg4maVxJq0LGh88CkkBlrywgowuMp0&expiration_timestamp=1620905607&email=testemail%40example.com"
        )

    @pytest.mark.features(USE_UNIVERSAL_LINKS=False)
    def test_generate_firebase_dynamic_link_without_params(self):
        url = urls.generate_app_link(path="signup-confirmation", params=None)
        assert url == (
            "https://passcultureapptestauto.page.link/?link=https%3A%2F%2Fwebapp-v2.example.com%2Fsignup-confirmation"
        )

    @pytest.mark.features(USE_UNIVERSAL_LINKS=False)
    def test_generate_firebase_dynamic_link_with_params(self):
        url = urls.generate_app_link(
            path="signup-confirmation",
            params={
                "token": "2sD3hu6DRhqhqeg4maVxJq0LGh88CkkBlrywgowuMp0",
                "expiration_timestamp": "1620905607",
                "email": "testemail@example.com",
            },
        )
        assert url == (
            "https://passcultureapptestauto.page.link/"
            "?link=https%3A%2F%2Fwebapp-v2.example.com%2Fsignup-confirmation%3F"
            "token%3D2sD3hu6DRhqhqeg4maVxJq0LGh88CkkBlrywgowuMp0%26expiration_timestamp%3D1620905607"
            "%26email%3Dtestemail%2540example.com"
        )


@pytest.mark.settings(PRO_URL="http://pcpro.com")
def test_build_pc_pro_offer_link():
    offer = offers_factories.OfferFactory.build(id=123)

    url = urls.build_pc_pro_offer_link(offer)

    assert url == f"http://pcpro.com/offre/individuelle/{offer.id}/recapitulatif"
