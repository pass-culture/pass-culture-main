import datetime
from unittest.mock import patch

import pytest

from pcapi.connectors.cine_digital_service import ResourceCDS
import pcapi.connectors.serialization.cine_digital_service_serializers as cds_serializers
from pcapi.core.booking_providers.cds.client import CineDigitalServiceAPI
import pcapi.core.booking_providers.cds.exceptions as cds_exceptions


class CineDigitalServiceGetShowTest:
    @patch("pcapi.core.booking_providers.cds.client.get_resource")
    def test_should_return_show_corresponding_to_show_id(self, mocked_get_resource):
        # Given
        cinema_id = "cinemaid_test"
        token = "token_test"
        api_url = "apiUrl_test/"
        resource = ResourceCDS.SHOWS

        json_shows = [
            {
                "id": 1,
                "internet_remaining_place": 10,
                "showtime": datetime.datetime(2022, 3, 28),
                "is_cancelled": False,
                "is_deleted": False,
            },
            {
                "id": 2,
                "internet_remaining_place": 30,
                "showtime": datetime.datetime(2022, 3, 29),
                "is_cancelled": False,
                "is_deleted": False,
            },
            {
                "id": 3,
                "internet_remaining_place": 100,
                "showtime": datetime.datetime(2022, 3, 30),
                "is_cancelled": False,
                "is_deleted": False,
            },
        ]
        mocked_get_resource.return_value = json_shows

        # when
        cine_digital_service = CineDigitalServiceAPI(
            cinema_id="cinemaid_test", token="token_test", api_url="apiUrl_test/"
        )
        show = cine_digital_service.get_show(2)

        # then
        mocked_get_resource.assert_called_once_with(api_url, cinema_id, token, resource)

        assert show.id == 2

    @patch("pcapi.core.booking_providers.cds.client.get_resource")
    def test_should_raise_exception_if_show_not_found(self, mocked_get_resource):
        json_shows = [
            {
                "id": 1,
                "internet_remaining_place": 10,
                "showtime": datetime.datetime(2022, 3, 28),
                "is_cancelled": False,
                "is_deleted": False,
            },
        ]
        mocked_get_resource.return_value = json_shows
        cine_digital_service = CineDigitalServiceAPI(cinema_id="test_id", token="token_test", api_url="test_url")
        with pytest.raises(cds_exceptions.CineDigitalServiceAPIException) as cds_exception:
            cine_digital_service.get_show(4)
        assert (
            str(cds_exception.value)
            == "Show #4 not found in Cine Digital Service API for cinemaId=test_id & url=test_url"
        )


class CineDigitalServiceGetPaymentTypeTest:
    @patch("pcapi.core.booking_providers.cds.client.get_resource")
    def test_should_return_pass_culture_payment_type(self, mocked_get_resource):
        payment_types = [
            cds_serializers.PaymentTypeCDS(
                id=21,
                active=True,
                shortlabel="PASSCULTURE",
            ),
            cds_serializers.PaymentTypeCDS(
                id=22,
                active=True,
                shortlabel="OTHERPAYMENTYPE",
            ),
        ]

        mocked_get_resource.return_value = payment_types
        cine_digital_service = CineDigitalServiceAPI(
            cinema_id="cinemaid_test", token="token_test", api_url="apiUrl_test"
        )

        payment_type = cine_digital_service.get_payment_type()

        assert payment_type.short_label == "PASSCULTURE"

    @patch("pcapi.core.booking_providers.cds.client.get_resource")
    def test_should_raise_exception_if_payment_type_not_found(self, mocked_get_resource):
        json_payment_types = [
            {
                "id": 23,
                "active": True,
                "shortlabel": "OTHERPAYMENTYPE2",
            },
            {
                "id": 22,
                "active": True,
                "shortlabel": "OTHERPAYMENTYPE",
            },
        ]
        mocked_get_resource.return_value = json_payment_types
        cine_digital_service = CineDigitalServiceAPI(cinema_id="test_id", token="token_test", api_url="test_url")
        with pytest.raises(cds_exceptions.CineDigitalServiceAPIException) as cds_exception:
            cine_digital_service.get_payment_type()
        assert (
            str(cds_exception.value)
            == "Pass Culture payment type not found in Cine Digital Service API for cinemaId=test_id & url=test_url"
        )


class CineDigitalServiceGetTariffTest:
    @patch("pcapi.core.booking_providers.cds.client.get_resource")
    def test_should_return_tariffs_with_pass_culture_tariff(self, mocked_get_resource):
        json_tariffs = [
            {
                "id": 1,
                "price": 10,
                "label": "Pass Culture 5€",
                "is_active": True,
            },
            {
                "id": 2,
                "price": 3.5,
                "label": "Other tariff",
                "is_active": True,
            },
        ]
        mocked_get_resource.return_value = json_tariffs
        cine_digital_service = CineDigitalServiceAPI(
            cinema_id="cinema_id_test", token="token_test", api_url="apiUrl_test"
        )
        tariff = cine_digital_service.get_tariff()

        assert tariff.label == "Pass Culture 5€"

    @patch("pcapi.core.booking_providers.cds.client.get_resource")
    def test_should_raise_exception_if_tariff_not_found(self, mocked_get_resource):
        json_tariffs = [
            {
                "id": 1,
                "price": 10,
                "label": "Another Tariff",
                "is_active": True,
            },
            {
                "id": 2,
                "price": 3.5,
                "label": "Other tariff",
                "is_active": True,
            },
        ]
        mocked_get_resource.return_value = json_tariffs
        cine_digital_service = CineDigitalServiceAPI(cinema_id="test_id", token="token_test", api_url="test_url")
        with pytest.raises(cds_exceptions.CineDigitalServiceAPIException) as cds_exception:
            cine_digital_service.get_tariff()
        assert (
            str(cds_exception.value)
            == "Tariff Pass Culture not found in Cine Digital Service API for cinemaId=test_id & url=test_url"
        )


class CineDigitalServiceGetScreenTest:
    @patch("pcapi.core.booking_providers.cds.client.get_resource")
    def test_should_return_screen_corresponding_to_screen_id(self, mocked_get_resource):
        json_screens = [
            {
                "id": 1,
                "seatmapfronttoback": True,
                "seatmaplefttoright": False,
                "seatmapskipmissingseats": False,
            },
            {
                "id": 2,
                "seatmapfronttoback": False,
                "seatmaplefttoright": True,
                "seatmapskipmissingseats": True,
            },
            {
                "id": 3,
                "seatmapfronttoback": True,
                "seatmaplefttoright": True,
                "seatmapskipmissingseats": True,
            },
        ]
        mocked_get_resource.return_value = json_screens
        cine_digital_service = CineDigitalServiceAPI(cinema_id="test_id", token="token_test", api_url="test_url")
        show = cine_digital_service.get_screen(2)

        assert show.id == 2

    @patch("pcapi.core.booking_providers.cds.client.get_resource")
    def test_should_raise_exception_if_screen_not_found(self, mocked_get_resource):
        json_screens = [
            {
                "id": 1,
                "seatmapfronttoback": True,
                "seatmaplefttoright": False,
                "seatmapskipmissingseats": False,
            },
            {
                "id": 2,
                "seatmapfronttoback": False,
                "seatmaplefttoright": True,
                "seatmapskipmissingseats": True,
            },
            {
                "id": 3,
                "seatmapfronttoback": True,
                "seatmaplefttoright": True,
                "seatmapskipmissingseats": True,
            },
        ]
        mocked_get_resource.return_value = json_screens
        cine_digital_service = CineDigitalServiceAPI(cinema_id="test_id", token="token_test", api_url="test_url")
        with pytest.raises(cds_exceptions.CineDigitalServiceAPIException) as cds_exception:
            cine_digital_service.get_screen(4)
        assert (
            str(cds_exception.value)
            == "Screen #4 not found in Cine Digital Service API for cinemaId=test_id & url=test_url"
        )


class CineDigitalServiceCancelBookingTest:
    @patch("pcapi.core.booking_providers.cds.client.put_resource")
    def test_should_cancel_booking_with_success(self, mocked_put_resource):
        # Given
        json_response = {}
        mocked_put_resource.return_value = json_response
        cine_digital_service = CineDigitalServiceAPI(cinema_id="test_id", token="token_test", api_url="test_url")

        # When
        try:
            cine_digital_service.cancel_booking(["3107362853729", "0312079646868"], 5)
        except cds_exceptions.CineDigitalServiceAPIException:
            assert False, "Should not raise exception"

    @patch("pcapi.core.booking_providers.cds.client.put_resource")
    def test_should_cancel_booking_with_errors_for_each_barcode(self, mocked_put_resource):
        # Given
        json_response = {
            "111111111111": "BARCODE_NOT_FOUND",
            "222222222222": "TICKET_ALREADY_CANCELED",
            "333333333333": "AFTER_END_OF_DAY",
            "444444444444": "AFTER_END_OF_SHOW",
            "555555555555": "DAY_CLOSED",
        }
        mocked_put_resource.return_value = json_response
        cine_digital_service = CineDigitalServiceAPI(cinema_id="test_id", token="token_test", api_url="test_url")

        # When
        with pytest.raises(cds_exceptions.CineDigitalServiceAPIException) as exception:
            cine_digital_service.cancel_booking(
                ["111111111111", "222222222222", "333333333333", "444444444444", "555555555555"], 5
            )
        sep = "\n"
        assert (
            str(exception.value)
            == f"""Error while canceling bookings :{sep}111111111111 : BARCODE_NOT_FOUND{sep}222222222222 : TICKET_ALREADY_CANCELED{sep}333333333333 : AFTER_END_OF_DAY{sep}444444444444 : AFTER_END_OF_SHOW{sep}555555555555 : DAY_CLOSED"""
        )
