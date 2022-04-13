from unittest import mock

from pcapi.connectors.cine_digital_service import ResourceCDS
from pcapi.connectors.cine_digital_service import _build_url
from pcapi.connectors.cine_digital_service import get_resource
from pcapi.core.testing import override_settings


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
