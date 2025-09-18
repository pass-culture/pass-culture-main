from unittest import mock

import pytest

import pcapi.core.external_bookings.cds.exceptions as cds_exceptions
from pcapi.connectors.cine_digital_service import ResourceCDS
from pcapi.connectors.cine_digital_service import _build_url
from pcapi.connectors.cine_digital_service import get_resource


class CineDigitalServiceBuildUrlTest:
    def test_build_url(self):
        cinema_id = "test_id"
        api_url = "test_url/"
        token = "test_token"
        resource = ResourceCDS.TARIFFS

        url = _build_url(api_url, cinema_id, token, resource)

        assert url == "https://test_id.test_url/tariffs?api_token=test_token"


class CineDigitalServiceGetResourceTest:
    @mock.patch("pcapi.connectors.cine_digital_service.requests.get")
    def test_should_return_shows_with_success(self, request_get):
        # Given
        cinema_id = "test_id"
        api_url = "test_url/"
        token = "test_token"
        resource = ResourceCDS.TARIFFS

        shows_json = [
            {
                "id": 1,
                "internetremainingplace": 10,
                "showtime": "2022-03-28T09:00:00.000+0100",
                "canceled": False,
                "deleted": False,
            },
            {
                "id": 2,
                "internetremainingplace": 30,
                "showtime": "2022-03-30T18:00:00.000+0100",
                "canceled": True,
                "deleted": False,
            },
        ]

        response_return_value = mock.MagicMock(status_code=200, text="")
        response_return_value.json = mock.MagicMock(return_value=shows_json)
        request_get.return_value = response_return_value

        # When
        json_data = get_resource(api_url, cinema_id, token, resource, request_timeout=14)

        # Then
        request_get.assert_called_once_with("https://test_id.test_url/tariffs?api_token=test_token", timeout=14)
        assert json_data == shows_json

    @mock.patch("pcapi.connectors.cine_digital_service.requests.get")
    def test_should_raise_if_error(self, request_get):
        # Given
        cinema_id = "test_id"
        api_url = "test_url/"
        token = "test_token"
        resource = ResourceCDS.TARIFFS

        request_get.return_value = mock.MagicMock(status_code=400, reason="the test token test_token is wrong")

        with pytest.raises(cds_exceptions.CineDigitalServiceAPIException) as exc_info:
            get_resource(api_url, cinema_id, token, resource, request_timeout=14)

        request_get.assert_called_once_with("https://test_id.test_url/tariffs?api_token=test_token", timeout=14)

        assert isinstance(exc_info.value, cds_exceptions.CineDigitalServiceAPIException)
        assert token not in str(exc_info.value)
        assert "Error on CDS API on GET ResourceCDS.TARIFFS" in str(exc_info.value)
