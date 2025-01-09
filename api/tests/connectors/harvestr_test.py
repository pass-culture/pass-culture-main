import pytest
from requests import HTTPError

from pcapi.connectors import harvestr


@pytest.mark.settings(ENV="pro", PRO_URL="https://passculture.pro")
class HarvestrConnectorTest:
    def test_create_message_success(self, requests_mock):
        requests_mock.post("https://rest.harvestr.io/v1/message")

        harvestr.create_message(
            title="Test",
            content="J'aimerais un petit miracle !",
            labels=["AC"],
            requester=harvestr.HaverstrRequester(name="Jean Pass", externalUid="345", email="jean@passculture.app"),
        )

        assert requests_mock.last_request.json() == {
            "integrationId": "pro",
            "integrationUrl": "https://passculture.pro",
            "channel": "FORM",
            "title": "Test",
            "content": "J'aimerais un petit miracle !",
            "labels": ["AC"],
            "requester": {
                "type": "USER",
                "name": "Jean Pass",
                "externalUid": "345",
                "email": "jean@passculture.app",
            },
        }

    def test_create_message_error(self, requests_mock):
        requests_mock.post("https://rest.harvestr.io/v1/message", status_code=501)

        with pytest.raises(HTTPError):
            harvestr.create_message(
                title="Test",
                content="J'aimerais un petit miracle !",
                labels=["AC"],
                requester=harvestr.HaverstrRequester(name="Jean Pass", externalUid="345", email="jean@passculture.app"),
            )
