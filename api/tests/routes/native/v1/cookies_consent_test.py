from datetime import datetime
import logging
import uuid

import pytest

from pcapi.core.users import factories as users_factories
from pcapi.routes.native.v1.serialization import cookies_consent as serializers


pytestmark = pytest.mark.usefixtures("db_session")

DEVICE_ID = str(uuid.uuid4())


@pytest.fixture(name="body")
def body_fixture() -> serializers.CookieConsentRequest:
    return {
        "consent": {
            "mandatory": [
                "firebase",
            ],
            "accepted": [
                "algolia search insight",
            ],
            "refused": [
                "amplitude",
                "batch",
            ],
        },
        "choiceDatetime": "2022-08-23T00:00:00",
        "deviceId": DEVICE_ID,
    }


class CookiesConsentTest:
    def test_post(self, client, body):
        response = client.post(
            "/native/v1/cookies_consent",
            json=body,
        )

        assert response.status_code == 204

    def test_user_id_can_be_given(self, client, body):
        user = users_factories.UserFactory()
        body["userId"] = user.id

        response = client.post("/native/v1/cookies_consent", json=body)

        assert response.status_code == 204

    def test_log_data(self, client, caplog, body):
        user = users_factories.UserFactory()
        body["userId"] = user.id

        with caplog.at_level(logging.INFO):
            response = client.post("/native/v1/cookies_consent", json=body)

            assert response.status_code == 204
            assert caplog.records[0].extra == {
                "consent": {
                    "mandatory": [
                        "firebase",
                    ],
                    "accepted": [
                        "algolia search insight",
                    ],
                    "refused": [
                        "amplitude",
                        "batch",
                    ],
                },
                "choice_datetime": datetime.fromisoformat("2022-08-23T00:00:00"),
                "device_id": DEVICE_ID,
                "user_id": user.id,
                "analyticsSource": "app-native",
            }
            assert caplog.records[0].technical_message_id == "cookies_consent"

    def test_invalid_data_structure(self, client):
        body = None

        response = client.post("/native/v1/cookies_consent", json=body)

        assert response.status_code == 400

    def test_missing_field_device_id(self, client, body):
        del body["deviceId"]

        response = client.post("/native/v1/cookies_consent", json=body)

        assert response.status_code == 400

    def test_missing_field_choice_datetime(self, client, body):
        del body["choiceDatetime"]

        response = client.post("/native/v1/cookies_consent", json=body)

        assert response.status_code == 400

    def test_missing_field_consent(self, client, body):
        del body["consent"]

        response = client.post("/native/v1/cookies_consent", json=body)

        assert response.status_code == 400

    def test_missing_field_mandatory(self, client, body):
        del body["consent"]["mandatory"]

        response = client.post("/native/v1/cookies_consent", json=body)

        assert response.status_code == 400

    def test_missing_field_accepted(self, client, body):
        del body["consent"]["accepted"]

        response = client.post("/native/v1/cookies_consent", json=body)

        assert response.status_code == 400

    def test_missing_field_refused(self, client, body):
        del body["consent"]["refused"]

        response = client.post("/native/v1/cookies_consent", json=body)

        assert response.status_code == 400

    def test_cookie_name_can_not_be_empty(self, client, body):
        body["consent"]["accepted"].append("")

        response = client.post("/native/v1/cookies_consent", json=body)

        assert response.status_code == 400

    def test_can_not_have_twice_the_same_cookie_name(self, client, body):
        body["consent"]["accepted"].append("batch")
        body["consent"]["accepted"].append("batch")

        response = client.post("/native/v1/cookies_consent", json=body)

        assert response.status_code == 400

    def test_can_reject_unknown_key(self, client, body):
        body["unknown"] = "value"

        response = client.post("/native/v1/cookies_consent", json=body)

        assert response.status_code == 400
