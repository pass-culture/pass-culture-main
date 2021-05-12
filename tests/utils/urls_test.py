from pcapi.utils.urls import generate_firebase_dynamic_link


class FirebaseLinksTest:
    def test_generate_firebase_dynamic_link(self):
        url = generate_firebase_dynamic_link(
            path="signup-confirmation",
            params={
                "token": "2sD3hu6DRhqhqeg4maVxJq0LGh88CkkBlrywgowuMp0",
                "expiration_timestamp": "1620905607",
                "email": "testemail@example.com",
            },
        )
        assert url == (
            "https://passcultureapptestauto.page.link/"
            "?link=https%3A%2F%2Fapp.passculture-testing.beta.gouv.fr%2Fsignup-confirmation%3F"
            "token%3D2sD3hu6DRhqhqeg4maVxJq0LGh88CkkBlrywgowuMp0%26expiration_timestamp%3D1620905607%26email%3Dtestemail%2540example.com"
        )
