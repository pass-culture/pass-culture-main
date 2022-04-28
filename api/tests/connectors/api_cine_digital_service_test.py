from unittest import mock

from pcapi.connectors.cine_digital_service import ResourceCDS
from pcapi.connectors.cine_digital_service import _build_url
from pcapi.connectors.cine_digital_service import get_resource
from pcapi.connectors.cine_digital_service import put_resource
from pcapi.connectors.serialization.cine_digital_service_serializers import CancelBookingCDS
from pcapi.core.testing import override_settings


class CineDigitalServiceBuildUrlTest:
    def test_build_url(self):
        cinema_id = "test_id"
        api_url = "test_url/"
        token = "test_token"
        resource = ResourceCDS.TARIFFS

        url = _build_url(api_url, cinema_id, token, resource)

        assert url == "https://test_id.test_url/tariffs?api_token=test_token"

    def test_build_url_with_path_params(self):
        cinema_id = "test_id"
        api_url = "test_url/"
        token = "test_token"
        resource = ResourceCDS.SEATMAP
        path_params = {"show_id": 1}

        url = _build_url(api_url, cinema_id, token, resource, path_params)

        assert url == "https://test_id.test_url/shows/1/seatmap?api_token=test_token"


class CineDigitalServiceGetResourceTest:
    @mock.patch("pcapi.connectors.cine_digital_service.requests.get")
    @override_settings(IS_DEV=False)
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
        json_data = get_resource(api_url, cinema_id, token, resource)

        # Then
        request_get.assert_called_once_with("https://test_id.test_url/tariffs?api_token=test_token")
        assert json_data == shows_json

    @mock.patch("pcapi.connectors.cine_digital_service.requests.get")
    @override_settings(IS_DEV=False)
    def should_call_url_with_path_params_if_present(self, request_get):
        # Given
        cinema_id = "test_id"
        api_url = "test_url/"
        token = "test_token"
        resource = ResourceCDS.SEATMAP
        path_params = {"show_id": 1}

        # When
        get_resource(api_url, cinema_id, token, resource, path_params)
        # Then
        request_get.assert_called_once_with("https://test_id.test_url/shows/1/seatmap?api_token=test_token")


class CineDigitalServicePutResourceTest:
    @mock.patch("pcapi.connectors.cine_digital_service.requests.put")
    @override_settings(IS_DEV=False)
    def test_should_return_shows_with_success(self, request_put):
        # Given
        cinema_id = "test_id"
        api_url = "test_url/"
        token = "test_token"
        resource = ResourceCDS.CANCEL_BOOKING
        body = CancelBookingCDS(barcodes=["111111111111"], paiementtypeid=5)

        response_json = {"111111111111": "BARCODE_NOT_FOUND"}

        response_return_value = mock.MagicMock(status_code=200, text="")
        response_return_value.json = mock.MagicMock(return_value=response_json)
        request_put.return_value = response_return_value

        # When
        json_data = put_resource(api_url, cinema_id, token, resource, body)

        # Then
        request_put.assert_called_once_with(
            "https://test_id.test_url/transaction/cancel?api_token=test_token",
            headers={"Content-Type": "application/json"},
            data='{"barcodes": ["111111111111"], "paiementtypeid": 5}',
        )
        assert json_data == response_json
