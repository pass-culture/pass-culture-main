import json
import logging
from unittest import mock

import pytest

from pcapi import settings
from pcapi.connectors.beneficiaries import ubble
from pcapi.core.subscription.ubble import schemas as ubble_schemas
from pcapi.core.users.models import GenderEnum
from pcapi.utils import requests

from tests.core.subscription.test_factories import UbbleIdentificationResponseFactory
from tests.core.subscription.ubble.end_to_end import fixtures
from tests.test_utils import json_default


class StartIdentificationTest:
    def test_start_identification(self, requests_mock):
        requests_mock.post(
            f"{settings.UBBLE_API_URL}/v2/create-and-start-idv",
            json=fixtures.ID_VERIFICATION_CREATION_RESPONSE,
        )

        response = ubble.create_and_start_identity_verification(
            first_name="Catherine",
            last_name="Destivelle",
            webhook_url="https://webhook.example.com",
            redirect_url="https://redirect.example.com",
        )

        assert isinstance(response, ubble_schemas.UbbleContent)
        assert requests_mock.call_count == 1
        assert requests_mock.last_request.json() == {
            "declared_data": {"name": "Catherine Destivelle"},
            "webhook_url": "https://webhook.example.com",
            "redirect_url": "https://redirect.example.com",
        }

    def test_start_identification_connection_error(self, requests_mock):
        requests_mock.post(f"{settings.UBBLE_API_URL}/v2/create-and-start-idv", exc=requests.exceptions.ConnectionError)

        with pytest.raises(ubble.UbbleHttpError):
            ubble.create_and_start_identity_verification(
                first_name="Cassandre",
                last_name="Beaugrand",
                webhook_url="https://webhook.example.com",
                redirect_url="https://redirect.example.com",
            )

        assert requests_mock.call_count == 1

    def test_start_identification_http_error_status(self, requests_mock):
        requests_mock.post(f"{settings.UBBLE_API_URL}/v2/create-and-start-idv", status_code=401)

        with pytest.raises(ubble.UbbleHttpError):
            ubble.create_and_start_identity_verification(
                first_name="Cassandre",
                last_name="Beaugrand",
                webhook_url="https://webhook.example.com",
                redirect_url="https://redirect.example.com",
            )

        assert requests_mock.call_count == 1


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


class RateLimitTest:
    @pytest.mark.settings(UBBLE_RATE_LIMIT=1)
    def test_start_identification_rate_limit(self, requests_mock):
        requests_mock.post(
            f"{settings.UBBLE_API_URL}/v2/create-and-start-idv",
            json=fixtures.ID_VERIFICATION_CREATION_RESPONSE,
        )

        ubble.create_and_start_identity_verification(
            first_name="Catherine",
            last_name="Destivelle",
            webhook_url="https://webhook.example.com",
            redirect_url="https://redirect.example.com",
        )

        with pytest.raises(ubble.UbbleRateLimitedError):
            ubble.create_and_start_identity_verification(
                first_name="Catherine",
                last_name="Destivelle",
                webhook_url="https://webhook.example.com",
                redirect_url="https://redirect.example.com",
            )
