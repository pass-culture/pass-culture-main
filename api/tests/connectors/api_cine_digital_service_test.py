from datetime import datetime
from datetime import timedelta
from datetime import timezone
from unittest import mock

import pytest

from pcapi.connectors.cine_digital_service import get_shows
import pcapi.core.booking_providers.cds.exceptions as cds_exceptions
from pcapi.core.testing import override_settings


class CineDigitalServiceGetShowsTest:
    @mock.patch("pcapi.connectors.cine_digital_service.requests.get")
    @override_settings(IS_DEV=False)
    def test_should_return_all_necessary_attributes(self, request_get):
        # Given
        cinema_id = "test_id"
        url = "test_url"
        token = "test_token"
        shows_json = [
            {
                "id": 1,
                "internetremainingplace": 10,
                "showtime": "2022-03-28T09:00:00.000+0100",
                "canceled": True,
                "deleted": False,
            },
        ]

        response_return_value = mock.MagicMock(status_code=200, text="")
        response_return_value.json = mock.MagicMock(return_value=shows_json)
        request_get.return_value = response_return_value

        # When
        shows = get_shows(cinema_id, url, token)

        # Then
        assert len(shows) == 1
        assert shows[0].id == 1
        assert shows[0].internet_remaining_place == 10
        assert shows[0].showtime == datetime(2022, 3, 28, 9, tzinfo=timezone(timedelta(seconds=3600)))
        assert shows[0].is_cancelled
        assert not shows[0].is_deleted

    @mock.patch("pcapi.connectors.cine_digital_service.requests.get")
    @override_settings(IS_DEV=False)
    def test_should_return_shows_with_success(self, request_get):
        # Given
        cinema_id = "test_id"
        url = "test_url"
        token = "test_token"
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
        shows = get_shows(cinema_id, url, token)

        # Then
        request_get.assert_called_once_with(f"https://{cinema_id}.{url}shows?api_token={token}")
        assert len(shows) == 2

    @mock.patch("pcapi.connectors.cine_digital_service.requests.get")
    @override_settings(IS_DEV=False)
    def test_should_raise_exception_when_api_call_fails(self, request_get):
        # Given
        cinema_id = "test_id"
        url = "test_url"
        token = "test_token"
        response_return_value = mock.MagicMock(status_code=400, text="")
        request_get.return_value = response_return_value

        # When
        with pytest.raises(cds_exceptions.CineDigitalServiceAPIException) as exception:
            get_shows(cinema_id, url, token)

        # Then
        assert (
            str(exception.value) == f"Error getting Cine Digital Service API DATA for cinemaId={cinema_id} & url={url}"
        )

    @mock.patch("pcapi.connectors.cine_digital_service.requests.get", side_effect=Exception)
    @override_settings(IS_DEV=False)
    def test_should_raise_exception_when_api_call_fails_with_connection_error(self, request_get):
        # Given
        cinema_id = "test_id"
        url = "test_url"
        token = "test_token"

        # When
        with pytest.raises(cds_exceptions.CineDigitalServiceAPIException) as cds_exception:
            get_shows(cinema_id, url, token)

        # Then
        assert str(cds_exception.value) == f"Error connecting CDS for cinemaId={cinema_id} & url={url}"
