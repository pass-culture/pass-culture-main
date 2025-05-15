import logging
import uuid
from datetime import datetime

import pytest

from pcapi.routes.shared import cookies_consent as serializers


pytestmark = pytest.mark.usefixtures("db_session")

DEVICE_ID = str(uuid.uuid4())


@pytest.fixture(name="body")
def body_fixture() -> serializers.CookieConsentRequest:
    return {
        "consent": {
            "mandatory": [
                "sentry",
            ],
            "accepted": [
                "firebase",
            ],
            "refused": [
                "hotjar",
                "beamer",
            ],
        },
        "choiceDatetime": "2022-08-23T00:00:00",
        "deviceId": DEVICE_ID,
    }


class CookiesConsentTest:
    def test_post(self, client, body):
        response = client.post(
            "/users/cookies",
            json=body,
        )

        assert response.status_code == 204

    def test_log_data(self, client, caplog, body):
        with caplog.at_level(logging.INFO):
            response = client.post("/users/cookies", json=body)

            assert response.status_code == 204
            assert caplog.records[0].extra == {
                "consent": {
                    "mandatory": [
                        "sentry",
                    ],
                    "accepted": [
                        "firebase",
                    ],
                    "refused": [
                        "hotjar",
                        "beamer",
                    ],
                },
                "choice_datetime": datetime.fromisoformat("2022-08-23T00:00:00"),
                "device_id": DEVICE_ID,
                "analyticsSource": "app-pro",
                "user_id": None,
            }
            assert caplog.records[0].technical_message_id == "cookies_consent"

    def test_can_not_have_twice_the_same_cookie_name(self, client, body):
        body["consent"]["accepted"].append("batch")
        body["consent"]["accepted"].append("batch")

        response = client.post("/users/cookies", json=body)

        assert response.status_code == 400

    def test_can_reject_unknown_key(self, client, body):
        body["unknown"] = "value"

        response = client.post("/users/cookies", json=body)

        assert response.status_code == 400
