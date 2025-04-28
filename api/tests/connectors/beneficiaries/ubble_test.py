import json
import logging
from unittest import mock

import pytest

from pcapi import settings
from pcapi.connectors.beneficiaries import ubble
from pcapi.core.fraud import models as fraud_models
from pcapi.core.users.models import GenderEnum
from pcapi.utils import requests

from tests.core.subscription.test_factories import UbbleIdentificationResponseFactory
from tests.test_utils import json_default


class StartIdentificationV2Test:
    @pytest.mark.features(WIP_UBBLE_V2=True)
    def test_start_identification(self, requests_mock, caplog):
        requests_mock.post(
            f"{settings.UBBLE_API_URL}/v2/create-and-start-idv",
            json={
                "id": "idv_01j9kndq7ry69dkd8j7hxrqfa8",
                "user_journey_id": "usj_01h13smebsb2y1tyyrzx1sgma7",
                "applicant_id": "aplt_01j9kndq6gcbj26jwh9b3njmhn",
                "webhook_url": "https://webhook.example.com",
                "redirect_url": "https://redirect.example.com",
                "declared_data": {"name": "Cassandre Beaugrand"},
                "created_on": "2024-10-07T14:16:38.908026Z",
                "modified_on": "2024-10-07T14:16:39.106564Z",
                "status": "pending",
                "response_codes": [],
                "documents": [],
                "_links": {
                    "self": {
                        "href": "https://api.ubble.example.com/v2/identity-verifications/idv_01j9kndq7ry69dkd8j7hxrqfa8"
                    },
                    "applicant": {
                        "href": "https://api.ubble.example.com/v2/applicants/aplt_01j9kndq6gcbj26jwh9b3njmhn"
                    },
                    "verification_url": {"href": "https://id.ubble.example.com/fa12e737-2a93-4608-9743-08fabd0b6f13"},
                },
            },
        )

        with caplog.at_level(logging.INFO):
            response = ubble.create_and_start_identity_verification(
                first_name="Cassandre",
                last_name="Beaugrand",
                webhook_url="https://webhook.example.com",
                redirect_url="https://redirect.example.com",
            )

        assert isinstance(response, fraud_models.UbbleContent)
        assert requests_mock.call_count == 1

        assert requests_mock.last_request.json() == {
            "declared_data": {"name": "Cassandre Beaugrand"},
            "webhook_url": "https://webhook.example.com",
            "redirect_url": "https://redirect.example.com",
        }

        assert len(caplog.records) >= 2
        record = caplog.records[2]
        assert record.extra["identification_id"] == str(response.identification_id)
        assert record.extra["request_type"] == "create-and-start-idv", record.extra
        assert record.message == "Valid response from Ubble"

    @pytest.mark.features(WIP_UBBLE_V2=True)
    def test_start_identification_connection_error(self, requests_mock, caplog):
        requests_mock.post(f"{settings.UBBLE_API_URL}/v2/create-and-start-idv", exc=requests.exceptions.ConnectionError)

        with pytest.raises(requests.ExternalAPIException):
            with caplog.at_level(logging.ERROR):
                ubble.create_and_start_identity_verification(
                    first_name="Cassandre",
                    last_name="Beaugrand",
                    webhook_url="https://webhook.example.com",
                    redirect_url="https://redirect.example.com",
                )

        assert requests_mock.call_count == 1

        assert len(caplog.records) == 1
        record = caplog.records[0]
        assert record.extra["request_type"] == "create-and-start-idv"
        assert record.extra["error_type"] == "network"
        assert record.message == "Ubble create-and-start-idv: Network error"

    @pytest.mark.features(WIP_UBBLE_V2=True)
    def test_start_identification_http_error_status(self, requests_mock, caplog):
        requests_mock.post(f"{settings.UBBLE_API_URL}/v2/create-and-start-idv", status_code=401)

        with pytest.raises(requests.ExternalAPIException):
            ubble.create_and_start_identity_verification(
                first_name="Cassandre",
                last_name="Beaugrand",
                webhook_url="https://webhook.example.com",
                redirect_url="https://redirect.example.com",
            )

        assert requests_mock.call_count == 1

        assert len(caplog.records) == 1
        record = caplog.records[0]
        assert record.extra["status_code"] == 401
        assert record.extra["request_type"] == "create-and-start-idv"
        assert record.extra["error_type"] == "http"
        assert record.message == "Ubble create-and-start-idv: Unexpected error: 401"


class StartIdentificationV1Test:
    def test_start_identification(self, ubble_mock, caplog):
        with caplog.at_level(logging.INFO):
            response = ubble.start_identification(
                user_id=123,
                first_name="prenom",
                last_name="nom",
                webhook_url="http://webhook/url/",
                redirect_url="http://redirect/url",
            )

        assert isinstance(response, fraud_models.UbbleContent)
        assert ubble_mock.call_count == 1

        attributes = ubble_mock.last_request.json()["data"]["attributes"]
        assert attributes["identification-form"]["external-user-id"] == 123
        assert attributes["identification-form"]["phone-number"] is None

        assert attributes["reference-data"]["first-name"] == "prenom"
        assert attributes["reference-data"]["last-name"] == "nom"
        assert attributes["webhook"] == "http://webhook/url/"
        assert attributes["redirect_url"] == "http://redirect/url"

        assert len(caplog.records) >= 1
        record = caplog.records[1]
        assert record.extra["status_code"] == 201
        assert record.extra["identification_id"] == str(response.identification_id)
        assert record.extra["request_type"] == "start-identification"
        assert record.message == "Valid response from Ubble"

    def test_start_identification_connection_error(self, ubble_mock_connection_error, caplog):
        with pytest.raises(requests.ExternalAPIException):
            with caplog.at_level(logging.ERROR):
                ubble.start_identification(
                    user_id=123,
                    first_name="prenom",
                    last_name="nom",
                    webhook_url="http://webhook/url/",
                    redirect_url="http://redirect/url",
                )

        assert ubble_mock_connection_error.call_count == 1
        assert len(caplog.records) == 1
        record = caplog.records[0]
        assert record.extra["request_type"] == "start-identification"
        assert record.extra["error_type"] == "network"
        assert record.message == "Ubble start-identification: Network error"

    def test_start_identification_http_error_status(self, ubble_mock_http_error_status, caplog):
        with pytest.raises(requests.ExternalAPIException):
            ubble.start_identification(
                user_id=123,
                first_name="prenom",
                last_name="nom",
                webhook_url="http://webhook/url/",
                redirect_url="http://redirect/url",
            )

        assert ubble_mock_http_error_status.call_count == 1
        assert len(caplog.records) == 1
        record = caplog.records[0]
        assert record.extra["status_code"] == 401
        assert record.extra["request_type"] == "start-identification"
        assert record.extra["error_type"] == "http"
        assert record.message == "Ubble start-identification: Unexpected error: 401, "


class ShouldUseMockTest:
    @pytest.mark.settings(UBBLE_MOCK_API_URL="")
    @mock.patch("pcapi.utils.requests.get")
    def test_return_early_false_if_mock_url_not_defined(self, mock_get):
        result = ubble._should_use_mock("id")

        assert result is False
        assert mock_get.call_count == 0

    @pytest.mark.settings(UBBLE_MOCK_API_URL="http://mock-ubble.com")
    @mock.patch("pcapi.utils.requests.get")
    def test_return_early_false_if_id_not_provided(self, mock_get):
        result = ubble._should_use_mock()

        assert result is False
        assert mock_get.call_count == 0

    @pytest.mark.settings(UBBLE_MOCK_API_URL="http://mock-ubble.com")
    @pytest.mark.parametrize("id_,status_code,expected_result", [("whatever", 200, True), ("whatever", 404, False)])
    @mock.patch("pcapi.utils.requests.get")
    def test_calls_mock_route_and_decide_base_url(self, mock_get, id_, status_code, expected_result):
        get_configuration_response = requests.Response()
        get_configuration_response.status_code = status_code
        mock_get.return_value = get_configuration_response

        result = ubble._should_use_mock(id_=id_)

        assert mock_get.call_count == 1
        assert len(mock_get.call_args.args) == 1
        assert mock_get.call_args.args[0] == f"http://mock-ubble.com/id_exists/{id_}"
        assert result is expected_result


class BuildUrlTest:
    @pytest.mark.settings(UBBLE_API_URL="http://example.com/partial/path")
    def test_add_slash_if_missing(self):
        url = ubble.build_url("and/end")

        assert url == "http://example.com/partial/path/and/end"

    @pytest.mark.settings(UBBLE_API_URL="http://example.com/partial/path")
    def test_dont_add_slash_if_given(self):
        url = ubble.build_url("/and/end")

        assert url == "http://example.com/partial/path/and/end"

    @pytest.mark.settings(UBBLE_API_URL="http://example.com/partial/path/")
    def test_remove_slash_if_given_twice(self):
        url = ubble.build_url("/and/end")

        assert url == "http://example.com/partial/path/and/end"


class GetContentTest:
    def test_get_content(self, ubble_mocker, caplog):
        ubble_response = UbbleIdentificationResponseFactory()
        with ubble_mocker(
            ubble_response.data.attributes.identification_id,
            json.dumps(ubble_response.dict(by_alias=True), sort_keys=True, default=json_default),
        ):
            with caplog.at_level(logging.INFO):
                ubble.get_content(ubble_response.data.attributes.identification_id)

            assert caplog.records[0].message == "External service called"

            supervision_record = caplog.records[1]
            assert supervision_record.message == "Valid response from Ubble"
            assert supervision_record.extra["status_code"] == 200
            assert supervision_record.extra["identification_id"] == ubble_response.data.attributes.identification_id
            assert supervision_record.extra["status"] == ubble_response.data.attributes.status.value
            assert not supervision_record.extra["score"]
            assert supervision_record.extra["request_type"] == "get-content"

    def test_get_content_http_error(self, requests_mock, caplog):
        identification_id = "some-id"
        requests_mock.register_uri("GET", f"/identifications/{identification_id}/", status_code=401)

        with caplog.at_level(logging.ERROR):
            with pytest.raises(requests.ExternalAPIException) as exc_info:
                ubble.get_content(identification_id)

        assert len(caplog.records) == 1
        record = caplog.records[0]
        assert record.message == "Ubble get-content: Unexpected error: 401, "
        assert record.extra["status_code"] == 401
        assert record.extra["identification_id"] == identification_id
        assert record.extra["request_type"] == "get-content"
        assert record.extra["error_type"] == "http"
        assert exc_info.value.is_retryable is False

    def test_get_content_network_error(self, requests_mock, caplog):
        identification_id = "some-id"
        requests_mock.register_uri("GET", f"/identifications/{identification_id}/", status_code=503)

        with caplog.at_level(logging.ERROR):
            with pytest.raises(requests.ExternalAPIException) as exc_info:
                ubble.get_content(identification_id)

        assert len(caplog.records) == 1
        record = caplog.records[0]
        assert record.message == "Ubble get-content: External error: 503"
        assert record.extra["status_code"] == 503
        assert record.extra["identification_id"] == identification_id
        assert record.extra["request_type"] == "get-content"
        assert record.extra["error_type"] == "http"
        assert exc_info.value.is_retryable is True


class HelperFunctionsTest:
    @pytest.mark.parametrize(
        "ubble_gender, expected",
        [
            ("M", GenderEnum.M),
            ("F", GenderEnum.F),
            ("X", None),
            (None, None),
        ],
    )
    def test_parse_ubble_gender(self, ubble_gender, expected):
        assert ubble._parse_ubble_gender(ubble_gender) == expected


class CreateIdentityVerificationAttemptTest:
    @pytest.mark.features(WIP_UBBLE_V2=True)
    def test_create_attempt_success(self, requests_mock, caplog):
        identification_id = "idv_01j9kndq7ry69dkd8j7hxrqfa8"
        requests_mock.post(
            f"{settings.UBBLE_API_URL}/v2/identity-verifications/{identification_id}/attempts",
            json={
                "id": "att_01j9kndq7ry69dkd8j7hxrqfa8",
                "_links": {
                    "verification_url": {"href": "https://id.ubble.example.com/new-attempt"},
                    "self": {
                        "href": f"https://api.ubble.example.com/v2/identity-verifications/{identification_id}/attempts/att_01j9kndq7ry69dkd8j7hxrqfa8"
                    },
                },
            },
        )

        with caplog.at_level(logging.INFO):
            url = ubble.create_identity_verification_attempt(
                identification_id=identification_id,
                redirect_url="https://redirect.example.com",
            )

        assert url == "https://id.ubble.example.com/new-attempt"
        assert requests_mock.call_count == 1
        assert requests_mock.last_request.json() == {"redirect_url": "https://redirect.example.com"}

        assert len(caplog.records) >= 2
        record = caplog.records[1]
        assert record.extra["identification_id"] == "att_01j9kndq7ry69dkd8j7hxrqfa8"
        assert record.message == "Ubble identification attempted"

    @pytest.mark.features(WIP_UBBLE_V2=True)
    def test_create_attempt_conflict(self, requests_mock, caplog):
        identification_id = "idv_01j9kndq7ry69dkd8j7hxrqfa8"
        # Mock the 409 error on attempt creation
        requests_mock.post(
            f"{settings.UBBLE_API_URL}/v2/identity-verifications/{identification_id}/attempts",
            status_code=409,
        )
        # Mock the get verification response
        requests_mock.get(
            f"{settings.UBBLE_API_URL}/v2/identity-verifications/{identification_id}",
            json={
                "id": identification_id,
                "user_journey_id": "usj_01h13smebsb2y1tyyrzx1sgma7",
                "applicant_id": "aplt_01j9kndq6gcbj26jwh9b3njmhn",
                "webhook_url": "https://webhook.example.com",
                "redirect_url": "https://redirect.example.com",
                "declared_data": {"name": "John Doe"},
                "created_on": "2024-10-07T14:16:38.908026Z",
                "modified_on": "2024-10-07T14:16:39.106564Z",
                "status": "pending",
                "response_codes": [],
                "documents": [],
                "_links": {
                    "self": {"href": f"https://api.ubble.example.com/v2/identity-verifications/{identification_id}"},
                    "verification_url": {"href": "https://id.ubble.example.com/existing-attempt"},
                },
            },
        )

        with caplog.at_level(logging.INFO):
            url = ubble.create_identity_verification_attempt(
                identification_id=identification_id,
                redirect_url="https://redirect.example.com",
            )

        assert url == "https://id.ubble.example.com/existing-attempt"
        assert requests_mock.call_count == 2  # One POST attempt + one GET for existing verification

        assert len(caplog.records) >= 2
        record = caplog.records[1]
        assert record.message == "An attempt already exists for this verification"
        assert record.extra["identification_id"] == identification_id

    @pytest.mark.features(WIP_UBBLE_V2=True)
    def test_create_attempt_other_error(self, requests_mock, caplog):
        identification_id = "idv_01j9kndq7ry69dkd8j7hxrqfa8"
        requests_mock.post(
            f"{settings.UBBLE_API_URL}/v2/identity-verifications/{identification_id}/attempts",
            status_code=500,
        )

        with pytest.raises(requests.ExternalAPIException):
            ubble.create_identity_verification_attempt(
                identification_id=identification_id,
                redirect_url="https://redirect.example.com",
            )

        assert requests_mock.call_count == 1
