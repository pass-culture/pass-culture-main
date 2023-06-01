import datetime
import json
from unittest.mock import patch

import pytest

from pcapi.connectors.cine_digital_service import ResourceCDS
import pcapi.connectors.serialization.cine_digital_service_serializers as cds_serializers
import pcapi.core.bookings.factories as bookings_factories
from pcapi.core.external_bookings.cds.client import CineDigitalServiceAPI
import pcapi.core.external_bookings.cds.exceptions as cds_exceptions
import pcapi.core.users.factories as users_factories


def create_show_cds(
    id_: int = 1,
    is_cancelled: bool = False,
    is_deleted: bool = False,
    is_disabled_seatmap: bool = False,
    is_empty_seatmap: str | bool = False,
    remaining_place: int = 88,
    internet_remaining_place: int = 100,
    showtime: datetime.datetime = datetime.datetime.utcnow(),
    shows_tariff_pos_type_ids=None,
    screen_id: int = 50,
    media_id: int = 52,
) -> cds_serializers.ShowCDS:
    if shows_tariff_pos_type_ids is None:
        shows_tariff_pos_type_ids = []
    return cds_serializers.ShowCDS(
        id=id_,
        is_cancelled=is_cancelled,
        is_deleted=is_deleted,
        is_disabled_seatmap=is_disabled_seatmap,
        is_empty_seatmap=is_empty_seatmap,
        remaining_place=remaining_place,
        internet_remaining_place=internet_remaining_place,
        showtime=showtime,
        shows_tariff_pos_type_collection=[
            cds_serializers.ShowTariffCDS(tariff=cds_serializers.IdObjectCDS(id=show_tariff_id))
            for show_tariff_id in shows_tariff_pos_type_ids
        ],
        screen=cds_serializers.IdObjectCDS(id=screen_id),
        media=cds_serializers.IdObjectCDS(id=media_id),
    )


def create_screen_cds(
    id_: int = 50,
    seatmap_front_to_back: bool = True,
    seatmap_left_to_right: bool = True,
    seatmap_skip_missing_seats: bool = False,
) -> cds_serializers.ScreenCDS:
    return cds_serializers.ScreenCDS(
        id=id_,
        seatmap_front_to_back=seatmap_front_to_back,
        seatmap_left_to_right=seatmap_left_to_right,
        seatmap_skip_missing_seats=seatmap_skip_missing_seats,
    )


class CineDigitalServiceGetShowTest:
    @patch("pcapi.core.external_bookings.cds.client.get_resource")
    def test_should_return_show_corresponding_to_show_id(self, mocked_get_resource):
        # Given
        token = "token_test"
        api_url = "apiUrl_test/"
        account_id = "accountid_test"
        resource = ResourceCDS.SHOWS

        json_shows = [
            {
                "id": 1,
                "remaining_place": 88,
                "internet_remaining_place": 10,
                "disableseatmap": False,
                "is_empty_seatmap": False,
                "showtime": datetime.datetime(2022, 3, 28),
                "is_cancelled": False,
                "is_deleted": False,
                "showsTariffPostypeCollection": [
                    {"tariffid": {"id": 96}},
                    {"tariffid": {"id": 3}},
                    {"tariffid": {"id": 2}},
                ],
                "screenid": {"id": 10},
                "mediaid": {"id": 52},
            },
            {
                "id": 2,
                "remaining_place": 88,
                "internet_remaining_place": 30,
                "disableseatmap": False,
                "is_empty_seatmap": False,
                "showtime": datetime.datetime(2022, 3, 29),
                "is_cancelled": False,
                "is_deleted": False,
                "showsTariffPostypeCollection": [
                    {"tariffid": {"id": 96}},
                ],
                "screenid": {"id": 10},
                "mediaid": {"id": 52},
            },
            {
                "id": 3,
                "remaining_place": 88,
                "internet_remaining_place": 100,
                "disableseatmap": False,
                "is_empty_seatmap": False,
                "showtime": datetime.datetime(2022, 3, 30),
                "is_cancelled": False,
                "is_deleted": False,
                "showsTariffPostypeCollection": [{"tariffid": {"id": 96}}],
                "screenid": {"id": 20},
                "mediaid": {"id": 52},
            },
        ]
        mocked_get_resource.return_value = json_shows

        # when
        cine_digital_service = CineDigitalServiceAPI(
            cinema_id="cinemaid_test",
            account_id="accountid_test",
            cinema_api_token="token_test",
            api_url="apiUrl_test/",
        )
        show = cine_digital_service.get_show(2)

        # then
        mocked_get_resource.assert_called_once_with(api_url, account_id, token, resource)

        assert show.id == 2

    @patch("pcapi.core.external_bookings.cds.client.get_resource")
    def test_should_raise_exception_if_show_not_found(self, mocked_get_resource):
        json_shows = [
            {
                "id": 1,
                "remaining_place": 88,
                "internet_remaining_place": 10,
                "disableseatmap": False,
                "is_empty_seatmap": False,
                "showtime": datetime.datetime(2022, 3, 28),
                "is_cancelled": False,
                "is_deleted": False,
                "showsTariffPostypeCollection": [{"tariffid": {"id": 96}}],
                "screenid": {"id": 10},
                "mediaid": {"id": 52},
            },
        ]
        mocked_get_resource.return_value = json_shows
        cine_digital_service = CineDigitalServiceAPI(
            cinema_id="test_id", account_id="account_test", cinema_api_token="token_test", api_url="test_url"
        )
        with pytest.raises(cds_exceptions.CineDigitalServiceAPIException) as cds_exception:
            cine_digital_service.get_show(4)
        assert (
            str(cds_exception.value)
            == "Show #4 not found in Cine Digital Service API for cinemaId=test_id & url=test_url"
        )

    @patch("pcapi.core.external_bookings.cds.client.get_resource")
    def test_should_return_true_if_seatmap_is_empty(self, mocked_get_resource):
        json_shows = [
            {
                "id": 1,
                "remaining_place": 88,
                "internet_remaining_place": 10,
                "disableseatmap": False,
                "seatmap": "[[]]",
                "showtime": datetime.datetime(2022, 3, 28),
                "is_cancelled": False,
                "is_deleted": False,
                "showsTariffPostypeCollection": [{"tariffid": {"id": 96}}],
                "screenid": {"id": 10},
                "mediaid": {"id": 52},
            },
        ]
        mocked_get_resource.return_value = json_shows
        cine_digital_service = CineDigitalServiceAPI(
            cinema_id="test_id", account_id="account_test", cinema_api_token="token_test", api_url="test_url"
        )
        show = cine_digital_service.get_show(1)
        assert show.is_empty_seatmap is True

    @patch("pcapi.core.external_bookings.cds.client.get_resource")
    def test_should_return_false_if_seatmap_is_not_empty(self, mocked_get_resource):
        json_shows = [
            {
                "id": 1,
                "remaining_place": 88,
                "internet_remaining_place": 10,
                "disableseatmap": False,
                "seatmap": "[[1,1,1,1],[2,2,2,2]]",
                "showtime": datetime.datetime(2022, 3, 28),
                "is_cancelled": False,
                "is_deleted": False,
                "showsTariffPostypeCollection": [{"tariffid": {"id": 96}}],
                "screenid": {"id": 10},
                "mediaid": {"id": 52},
            },
        ]
        mocked_get_resource.return_value = json_shows
        cine_digital_service = CineDigitalServiceAPI(
            cinema_id="test_id", account_id="account_test", cinema_api_token="token_test", api_url="test_url"
        )
        show = cine_digital_service.get_show(1)
        assert show.is_empty_seatmap is False


class CineDigitalServiceGetShowsRemainingPlacesTest:
    @patch("pcapi.core.external_bookings.cds.client.get_resource")
    @patch(
        "pcapi.core.external_bookings.cds.client.CineDigitalServiceAPI.get_internet_sale_gauge_active",
        return_value=True,
    )
    def test_should_return_shows_id_with_corresponding_internet_remaining_places(
        self, mocked_internet_sale_gauge_active, mocked_get_resource
    ):
        # Given
        token = "token_test"
        api_url = "apiUrl_test/"
        account_id = "accountid_test"
        resource = ResourceCDS.SHOWS

        json_shows = [
            {
                "id": 1,
                "remaining_place": 88,
                "internet_remaining_place": 10,
                "disableseatmap": False,
                "is_empty_seatmap": False,
                "showtime": datetime.datetime(2022, 3, 28),
                "is_cancelled": False,
                "is_deleted": False,
                "showsTariffPostypeCollection": [
                    {"tariffid": {"id": 2}},
                ],
                "screenid": {"id": 10},
                "mediaid": {"id": 52},
            },
            {
                "id": 2,
                "remaining_place": 88,
                "internet_remaining_place": 30,
                "disableseatmap": False,
                "is_empty_seatmap": False,
                "showtime": datetime.datetime(2022, 3, 29),
                "is_cancelled": False,
                "is_deleted": False,
                "showsTariffPostypeCollection": [
                    {"tariffid": {"id": 2}},
                ],
                "screenid": {"id": 10},
                "mediaid": {"id": 52},
            },
            {
                "id": 3,
                "remaining_place": 88,
                "internet_remaining_place": 100,
                "disableseatmap": False,
                "is_empty_seatmap": False,
                "showtime": datetime.datetime(2022, 3, 30),
                "is_cancelled": False,
                "is_deleted": False,
                "showsTariffPostypeCollection": [
                    {"tariffid": {"id": 2}},
                ],
                "screenid": {"id": 10},
                "mediaid": {"id": 52},
            },
        ]
        mocked_get_resource.return_value = json_shows

        # when
        cine_digital_service = CineDigitalServiceAPI(
            cinema_id="cinemaid_test",
            account_id="accountid_test",
            cinema_api_token="token_test",
            api_url="apiUrl_test/",
        )
        shows_remaining_places = cine_digital_service.get_shows_remaining_places([2, 3])

        # then
        mocked_get_resource.assert_called_once_with(api_url, account_id, token, resource)

        assert shows_remaining_places == {2: 30, 3: 100}

    @patch("pcapi.core.external_bookings.cds.client.get_resource")
    @patch(
        "pcapi.core.external_bookings.cds.client.CineDigitalServiceAPI.get_internet_sale_gauge_active",
        return_value=False,
    )
    def test_should_return_shows_id_with_corresponding_remaining_places(
        self, mocked_internet_sale_gauge_active, mocked_get_resource
    ):
        # Given
        account_id = "accountid_test"
        token = "token_test"
        api_url = "apiUrl_test/"
        resource = ResourceCDS.SHOWS

        json_shows = [
            {
                "id": 1,
                "remaining_place": 88,
                "internet_remaining_place": 10,
                "disableseatmap": False,
                "is_empty_seatmap": False,
                "showtime": datetime.datetime(2022, 3, 28),
                "is_cancelled": False,
                "is_deleted": False,
                "showsTariffPostypeCollection": [
                    {"tariffid": {"id": 2}},
                ],
                "screenid": {"id": 10},
                "mediaid": {"id": 52},
            },
            {
                "id": 2,
                "remaining_place": 88,
                "internet_remaining_place": 30,
                "disableseatmap": False,
                "is_empty_seatmap": False,
                "showtime": datetime.datetime(2022, 3, 29),
                "is_cancelled": False,
                "is_deleted": False,
                "showsTariffPostypeCollection": [
                    {"tariffid": {"id": 2}},
                ],
                "screenid": {"id": 10},
                "mediaid": {"id": 52},
            },
            {
                "id": 3,
                "remaining_place": 88,
                "internet_remaining_place": 100,
                "disableseatmap": False,
                "is_empty_seatmap": False,
                "showtime": datetime.datetime(2022, 3, 30),
                "is_cancelled": False,
                "is_deleted": False,
                "showsTariffPostypeCollection": [
                    {"tariffid": {"id": 2}},
                ],
                "screenid": {"id": 10},
                "mediaid": {"id": 52},
            },
        ]
        mocked_get_resource.return_value = json_shows

        # when
        cine_digital_service = CineDigitalServiceAPI(
            cinema_id="cinemaid_test",
            account_id="accountid_test",
            cinema_api_token="token_test",
            api_url="apiUrl_test/",
        )
        shows_remaining_places = cine_digital_service.get_shows_remaining_places([2, 3])

        # then
        mocked_get_resource.assert_called_once_with(api_url, account_id, token, resource)

        assert shows_remaining_places == {2: 88, 3: 88}


class CineDigitalServiceGetPaymentTypeTest:
    @patch("pcapi.core.external_bookings.cds.client.get_resource")
    def test_should_return_voucher_payment_type(self, mocked_get_resource):
        json_payment_types = [
            {
                "id": 21,
                "active": True,
                "internalcode": "VCH",
            },
            {
                "id": 22,
                "active": True,
                "internalcode": "OTHERPAYMENTYPE",
            },
        ]

        mocked_get_resource.return_value = json_payment_types
        cine_digital_service = CineDigitalServiceAPI(
            cinema_id="cinemaid_test", account_id="accountid_test", cinema_api_token="token_test", api_url="apiUrl_test"
        )

        payment_type = cine_digital_service.get_voucher_payment_type()

        assert payment_type.id == 21
        assert payment_type.internal_code == "VCH"

    @patch("pcapi.core.external_bookings.cds.client.get_resource")
    def test_should_raise_exception_if_payment_type_not_found(self, mocked_get_resource):
        json_payment_types = [
            {
                "id": 23,
                "active": True,
                "internalcode": "OTHERPAYMENTYPE2",
            },
            {
                "id": 22,
                "active": True,
                "internalcode": "OTHERPAYMENTYPE",
            },
        ]
        mocked_get_resource.return_value = json_payment_types
        cine_digital_service = CineDigitalServiceAPI(
            cinema_id="test_id", account_id="accountid_test", cinema_api_token="token_test", api_url="test_url"
        )
        with pytest.raises(cds_exceptions.CineDigitalServiceAPIException) as cds_exception:
            cine_digital_service.get_voucher_payment_type()
        assert (
            str(cds_exception.value)
            == "Pass Culture payment type not found in Cine Digital Service API for cinemaId=test_id & url=test_url"
        )


class CineDigitalServiceGetPCVoucherTypesTest:
    @patch("pcapi.core.external_bookings.cds.client.get_resource")
    def test_should_return_only_voucher_types_with_pass_culture_code_and_tariff(self, mocked_get_resource):
        json_voucher_types = [
            {"id": 1, "code": "TESTCODE", "tariffid": {"id": 2, "price": 5, "active": True, "labeltariff": ""}},
            {"id": 2, "code": "PSCULTURE", "tariffid": {"id": 3, "price": 5, "active": True, "labeltariff": ""}},
            {"id": 3, "code": "PSCULTURE", "tariffid": {"id": 4, "price": 6, "active": True, "labeltariff": ""}},
            {"id": 4, "code": "PSCULTURE"},
            {"id": 5, "code": None},
        ]

        mocked_get_resource.return_value = json_voucher_types
        cine_digital_service = CineDigitalServiceAPI(
            cinema_id="cinema_id_test",
            account_id="accountid_test",
            cinema_api_token="token_test",
            api_url="apiUrl_test",
        )
        pc_voucher_types = cine_digital_service.get_pc_voucher_types()

        assert len(pc_voucher_types) == 2
        assert pc_voucher_types[0].id == 2
        assert pc_voucher_types[0].code == "PSCULTURE"
        assert pc_voucher_types[0].tariff.id == 3
        assert pc_voucher_types[0].tariff.price == 5
        assert pc_voucher_types[1].id == 3
        assert pc_voucher_types[1].tariff.id == 4


class CineDigitalServiceGetScreenTest:
    @patch("pcapi.core.external_bookings.cds.client.get_resource")
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
        cine_digital_service = CineDigitalServiceAPI(
            cinema_id="test_id", account_id="accountid_test", cinema_api_token="token_test", api_url="test_url"
        )
        show = cine_digital_service.get_screen(2)

        assert show.id == 2

    @patch("pcapi.core.external_bookings.cds.client.get_resource")
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
        cine_digital_service = CineDigitalServiceAPI(
            cinema_id="test_id", account_id="accountid_test", cinema_api_token="token_test", api_url="test_url"
        )
        with pytest.raises(cds_exceptions.CineDigitalServiceAPIException) as cds_exception:
            cine_digital_service.get_screen(4)
        assert (
            str(cds_exception.value)
            == "Screen #4 not found in Cine Digital Service API for cinemaId=test_id & url=test_url"
        )


class CineDigitalServiceGetAvailableSingleSeatTest:
    @patch("pcapi.core.external_bookings.cds.client.get_resource")
    @patch("pcapi.core.external_bookings.cds.client.CineDigitalServiceAPI.get_hardcoded_setmap", return_value=None)
    def test_should_return_seat_available(self, mocked_get_hardcoded_seatmap, mocked_get_resource):
        seatmap_json = [
            [1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1],
            [1, 3, 1, 1, 1, 1, 1, 1, 0, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1],
            [0, 0, 0, 1, 1, 1, 1, 1, 0, 1, 1],
        ]

        screen = cds_serializers.ScreenCDS(
            id=1,
            seatmapfronttoback=True,
            seatmaplefttoright=True,
            seatmapskipmissingseats=False,
        )

        show = create_show_cds(id_=1)

        mocked_get_resource.return_value = seatmap_json
        cine_digital_service = CineDigitalServiceAPI(
            cinema_id="test_id", account_id="accountid_test", cinema_api_token="token_test", api_url="test_url"
        )

        best_seat = cine_digital_service.get_available_seat(show, screen)
        assert len(best_seat) == 1
        assert best_seat[0].seatRow == 4
        assert best_seat[0].seatCol == 5
        assert best_seat[0].seatNumber == "E_6"

    @patch("pcapi.core.external_bookings.cds.client.get_resource")
    @patch("pcapi.core.external_bookings.cds.client.CineDigitalServiceAPI.get_hardcoded_setmap")
    def test_should_return_seat_available_when_seatmap_is_hardcoded(
        self, mocked_get_hardcoded_seatmap, mocked_get_resource
    ):
        seatmap_json = [
            [1, 1, 1, 1, 1, 1, 0, 1, 1],
            [1, 1, 1, 1, 1, 1, 0, 1, 1],
            [1, 1, 1, 1, 1, 1, 0, 1, 1],
        ]
        mocked_hardcoded_seatmap = '[["P_17","P_15","P_13","P_11","P_9","P_7","P_5","P_3","P_1"], ["M_17","M_15","M_13","M_11","M_9","M_7","M_5","M_3","M_1"], ["O_17","O_15","O_13","O_11","O_9","O_7","O_5","O_3","O_1"]]'

        mocked_get_hardcoded_seatmap.return_value = mocked_hardcoded_seatmap

        screen = cds_serializers.ScreenCDS(
            id=1,
            seatmapfronttoback=True,
            seatmaplefttoright=True,
            seatmapskipmissingseats=False,
        )

        show = create_show_cds(id_=1)

        mocked_get_resource.return_value = seatmap_json
        cine_digital_service = CineDigitalServiceAPI(
            cinema_id="test_id", account_id="accountid_test", cinema_api_token="token_test", api_url="test_url"
        )

        best_seat = cine_digital_service.get_available_seat(show, screen)
        assert len(best_seat) == 1
        assert best_seat[0].seatRow == 1
        assert best_seat[0].seatCol == 4
        assert best_seat[0].seatNumber == "M_9"

    @patch("pcapi.core.external_bookings.cds.client.get_resource")
    @patch("pcapi.core.external_bookings.cds.client.CineDigitalServiceAPI.get_hardcoded_setmap", return_value=None)
    def test_should_not_return_prm_seat(self, mocked_gat_hardcoded_seatmap, mocked_get_resource):
        seatmap_json = [
            [1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1],
            [1, 3, 1, 1, 1, 1, 1, 1, 0, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1],
            [1, 1, 11, 11, 11, 11, 11, 11, 0, 11, 11],
            [1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1],
            [0, 0, 0, 1, 1, 1, 1, 1, 0, 1, 1],
        ]

        screen = cds_serializers.ScreenCDS(
            id=1,
            seatmapfronttoback=True,
            seatmaplefttoright=True,
            seatmapskipmissingseats=False,
        )
        show = create_show_cds(id_=1, screen_id=1)
        mocked_get_resource.return_value = seatmap_json
        cine_digital_service = CineDigitalServiceAPI(
            cinema_id="test_id", account_id="accountid_test", cinema_api_token="token_test", api_url="test_url"
        )
        best_seat = cine_digital_service.get_available_seat(show, screen)
        assert len(best_seat) == 1
        assert best_seat[0].seatRow == 3
        assert best_seat[0].seatCol == 5
        assert best_seat[0].seatNumber == "D_6"

    @patch("pcapi.core.external_bookings.cds.client.get_resource")
    @patch("pcapi.core.external_bookings.cds.client.CineDigitalServiceAPI.get_hardcoded_setmap", return_value=None)
    def test_should_return_seat_infos_according_to_screen(self, mocked_gat_hardcoded_seatmap, mocked_get_resource):
        seatmap_json = [
            [3, 3, 3, 3, 0, 0, 3, 3],
            [3, 3, 3, 3, 0, 0, 3, 3],
            [3, 3, 3, 3, 0, 0, 3, 3],
            [3, 3, 3, 1, 0, 0, 3, 3],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [3, 3, 3, 3, 0, 0, 3, 3],
        ]

        screen = cds_serializers.ScreenCDS(
            id=1,
            seatmapfronttoback=False,
            seatmaplefttoright=False,
            seatmapskipmissingseats=True,
        )

        show = create_show_cds(id_=1, screen_id=1)

        mocked_get_resource.return_value = seatmap_json
        cine_digital_service = CineDigitalServiceAPI(
            cinema_id="test_id", account_id="accountid_test", cinema_api_token="token_test", api_url="test_url"
        )
        best_seat = cine_digital_service.get_available_seat(show, screen)
        assert len(best_seat) == 1
        assert best_seat[0].seatRow == 3
        assert best_seat[0].seatCol == 3
        assert best_seat[0].seatNumber == "B_3"

    @patch("pcapi.core.external_bookings.cds.client.get_resource")
    def test_should_return_None_if_no_seat_available(self, mocked_get_resource):
        seatmap_json = [
            [3, 3, 3, 3, 0, 3],
            [3, 3, 3, 3, 0, 3],
            [3, 3, 3, 3, 0, 3],
            [3, 3, 3, 3, 0, 3],
            [3, 3, 3, 3, 0, 3],
        ]

        screen = cds_serializers.ScreenCDS(
            id=1,
            seatmapfronttoback=True,
            seatmaplefttoright=True,
            seatmapskipmissingseats=False,
        )
        show = create_show_cds(id_=1, screen_id=1)

        mocked_get_resource.return_value = seatmap_json
        cine_digital_service = CineDigitalServiceAPI(
            cinema_id="test_id", account_id="accountid_test", cinema_api_token="token_test", api_url="test_url"
        )
        best_seat = cine_digital_service.get_available_seat(show, screen)
        assert not best_seat

    @patch("pcapi.core.external_bookings.cds.client.get_resource")
    @patch("pcapi.core.external_bookings.cds.client.CineDigitalServiceAPI.get_hardcoded_setmap", return_value=None)
    def test_should_return_correct_seat_number(self, mocked_gat_hardcoded_seatmap, mocked_get_resource):
        # fmt: off
        seatmap_json = [
            [0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1],  # A
            [0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1],  # B
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,],  # Empty row, No letter
            [1, 1, 0, 11, 1, 1, 0, 11, 0, 0, 0, 1, 11, 0, 1, 1, 1, 1, 0, 11, 1, 1, 1, 11, 0, 1, 1, 0, 0, 1, 1, 1, 1, 1],  # C
            [1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1],  # ...
            [1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 3, 3, 3, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 1, 1, 3, 3, 3, 3, 3, 3, 3, 3, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 1, 1, 3, 3, 3, 3, 3, 3, 3, 3, 3, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 1, 1, 1, 3, 3, 3, 3, 3, 3, 3, 3, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 3, 3, 3, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        ]
        # fmt: on

        screen = cds_serializers.ScreenCDS(
            id=1,
            seatmapfronttoback=True,
            seatmaplefttoright=False,
            seatmapskipmissingseats=False,
        )
        show = create_show_cds(id_=1, screen_id=1)

        mocked_get_resource.return_value = seatmap_json
        cine_digital_service = CineDigitalServiceAPI(
            cinema_id="test_id", account_id="accountid_test", cinema_api_token="token_test", api_url="test_url"
        )
        best_seat = cine_digital_service.get_available_seat(show, screen)
        assert best_seat[0].seatRow == 5
        assert best_seat[0].seatCol == 18
        assert best_seat[0].seatNumber == "E_16"


class CineDigitalServiceGetAvailableDuoSeatTest:
    @patch("pcapi.core.external_bookings.cds.client.CineDigitalServiceAPI.get_cinema_infos")
    @patch("pcapi.core.external_bookings.cds.client.CineDigitalServiceAPI.get_seatmap")
    def test_should_return_duo_seat_if_available(self, mocked_get_seatmap, mocked_get_cinema_infos):
        seatmap = cds_serializers.SeatmapCDS(
            __root__=[
                [1, 1, 1, 1, 0, 1],
                [1, 1, 1, 3, 0, 1],
                [1, 1, 3, 3, 0, 1],
                [1, 1, 3, 1, 0, 1],
                [1, 1, 1, 1, 0, 1],
            ]
        )

        cinema = cds_serializers.CinemaCDS(id=1, is_internet_sale_gauge_active=True)
        screen = cds_serializers.ScreenCDS(
            id=1,
            seatmapfronttoback=True,
            seatmaplefttoright=True,
            seatmapskipmissingseats=False,
        )
        show = create_show_cds(id_=1, screen_id=1)

        mocked_get_seatmap.return_value = seatmap
        mocked_get_cinema_infos.return_value = cinema
        cine_digital_service = CineDigitalServiceAPI(
            cinema_id="test_id", account_id="accountid_test", cinema_api_token="token_test", api_url="test_url"
        )
        duo_seats = cine_digital_service.get_available_duo_seat(show, screen)
        assert len(duo_seats) == 2
        assert duo_seats[0].seatNumber == "B_2"
        assert duo_seats[1].seatNumber == "B_3"

    @patch("pcapi.core.external_bookings.cds.client.CineDigitalServiceAPI.get_hardcoded_setmap")
    @patch("pcapi.core.external_bookings.cds.client.CineDigitalServiceAPI.get_seatmap")
    def test_should_return_duo_seat_if_available_when_seatmap_is_hardcoded(
        self, mocked_get_seatmap, mocked_get_hardcoded_setmap
    ):
        seatmap = cds_serializers.SeatmapCDS(
            __root__=[
                [1, 1, 1, 1, 0, 1],
                [1, 1, 1, 3, 0, 1],
            ]
        )
        mocked_hardcoded_seatmap = (
            '[["P_17","P_15","P_13","P_11","P_9","P_7"], ["M_17","M_15","M_13","M_11","M_9","M_7"]]'
        )
        screen = cds_serializers.ScreenCDS(
            id=1,
            seatmapfronttoback=True,
            seatmaplefttoright=True,
            seatmapskipmissingseats=False,
        )
        show = create_show_cds(id_=1, screen_id=1)

        mocked_get_seatmap.return_value = seatmap
        mocked_get_hardcoded_setmap.return_value = mocked_hardcoded_seatmap
        cine_digital_service = CineDigitalServiceAPI(
            cinema_id="test_id", account_id="accountid_test", cinema_api_token="token_test", api_url="test_url"
        )
        duo_seats = cine_digital_service.get_available_duo_seat(show, screen)
        assert len(duo_seats) == 2
        assert duo_seats[0].seatNumber == "P_13"
        assert duo_seats[1].seatNumber == "P_11"

    @patch("pcapi.core.external_bookings.cds.client.get_resource")
    def test_should_return_empty_if_less_than_two_seats_available(self, mocked_get_resource):
        seatmap_json = [
            [3, 3, 3, 3, 0, 1],
            [3, 3, 3, 3, 0, 3],
            [3, 3, 3, 3, 0, 3],
            [3, 3, 3, 3, 0, 3],
            [3, 3, 3, 3, 0, 3],
        ]

        screen = cds_serializers.ScreenCDS(
            id=1,
            seatmapfronttoback=True,
            seatmaplefttoright=True,
            seatmapskipmissingseats=False,
        )
        show = create_show_cds(id_=1, screen_id=1)

        mocked_get_resource.return_value = seatmap_json
        cine_digital_service = CineDigitalServiceAPI(
            cinema_id="test_id", account_id="accountid_test", cinema_api_token="token_test", api_url="test_url"
        )
        duo_seats = cine_digital_service.get_available_duo_seat(show, screen)
        assert len(duo_seats) == 0

    @patch("pcapi.core.external_bookings.cds.client.CineDigitalServiceAPI.get_cinema_infos")
    @patch("pcapi.core.external_bookings.cds.client.CineDigitalServiceAPI.get_seatmap")
    def test_should_return_two_separate_seats_if_no_duo_available(self, mocked_get_seatmap, mocked_get_cinema_infos):
        seatmap = cds_serializers.SeatmapCDS(
            __root__=[
                [1, 3, 1, 3, 0, 1],
                [3, 3, 3, 3, 0, 3],
                [1, 3, 1, 3, 0, 1],
                [3, 3, 1, 3, 0, 3],
                [3, 1, 3, 1, 0, 1],
            ]
        )

        screen = cds_serializers.ScreenCDS(
            id=1,
            seatmapfronttoback=True,
            seatmaplefttoright=True,
            seatmapskipmissingseats=False,
        )
        show = create_show_cds(id_=1, screen_id=1)
        cinema = cds_serializers.CinemaCDS(id=1, is_internet_sale_gauge_active=True)

        mocked_get_seatmap.return_value = seatmap
        mocked_get_cinema_infos.return_value = cinema
        cine_digital_service = CineDigitalServiceAPI(
            cinema_id="test_id", account_id="accountid_test", cinema_api_token="token_test", api_url="test_url"
        )
        duo_seats = cine_digital_service.get_available_duo_seat(show, screen)
        assert len(duo_seats) == 2
        assert duo_seats[0].seatNumber == "C_3"
        assert duo_seats[1].seatNumber == "D_3"


class CineDigitalServiceCancelBookingTest:
    @patch("pcapi.core.external_bookings.cds.client.put_resource")
    @patch("pcapi.core.external_bookings.cds.client.CineDigitalServiceAPI.get_voucher_payment_type")
    def test_should_cancel_booking_with_success(self, mocked_get_voucher_payment_type, mocked_put_resource):
        # Given
        json_response = {}
        mocked_put_resource.return_value = json_response
        mocked_get_voucher_payment_type.return_value = cds_serializers.PaymentTypeCDS(
            id=12, internal_code="VCH", is_active=True
        )
        cine_digital_service = CineDigitalServiceAPI(
            cinema_id="test_id", account_id="accountid_test", cinema_api_token="token_test", api_url="test_url"
        )

        # When
        try:
            cine_digital_service.cancel_booking(["3107362853729", "1312079646868"])
        except cds_exceptions.CineDigitalServiceAPIException:
            assert False, "Should not raise exception"

    @patch("pcapi.core.external_bookings.cds.client.put_resource")
    @patch("pcapi.core.external_bookings.cds.client.CineDigitalServiceAPI.get_voucher_payment_type")
    def test_should_cancel_booking_with_errors_for_each_barcode(
        self, mocked_get_voucher_payment_type, mocked_put_resource
    ):
        # Given
        json_response = {
            "111111111111": "BARCODE_NOT_FOUND",
            "222222222222": "TICKET_ALREADY_CANCELED",
            "333333333333": "AFTER_END_OF_DAY",
            "444444444444": "AFTER_END_OF_SHOW",
            "555555555555": "DAY_CLOSED",
        }
        mocked_put_resource.return_value = json_response
        mocked_get_voucher_payment_type.return_value = cds_serializers.PaymentTypeCDS(
            id=12, internal_code="VCH", is_active=True
        )
        cine_digital_service = CineDigitalServiceAPI(
            cinema_id="test_id", account_id="accountid_test", cinema_api_token="token_test", api_url="test_url"
        )

        # When
        with pytest.raises(cds_exceptions.CineDigitalServiceAPIException) as exception:
            cine_digital_service.cancel_booking(
                ["111111111111", "222222222222", "333333333333", "444444444444", "555555555555"]
            )
        sep = "\n"
        assert (
            str(exception.value)
            == f"""Error while canceling bookings :{sep}111111111111 : BARCODE_NOT_FOUND{sep}222222222222 : TICKET_ALREADY_CANCELED{sep}333333333333 : AFTER_END_OF_DAY{sep}444444444444 : AFTER_END_OF_SHOW{sep}555555555555 : DAY_CLOSED"""
        )

    @patch("pcapi.core.external_bookings.cds.client.put_resource")
    @patch("pcapi.core.external_bookings.cds.client.CineDigitalServiceAPI.get_voucher_payment_type")
    def test_should_not_raise_error_when_cancel_bookings_already_cancelled(
        self, mocked_get_voucher_payment_type, mocked_put_resource
    ):
        # Given
        json_response = {
            "111111111111": "TICKET_ALREADY_CANCELED",
            "222222222222": "TICKET_ALREADY_CANCELED",
            "333333333333": "TICKET_ALREADY_CANCELED",
        }
        mocked_put_resource.return_value = json_response
        mocked_get_voucher_payment_type.return_value = cds_serializers.PaymentTypeCDS(
            id=12, internal_code="VCH", is_active=True
        )
        cine_digital_service = CineDigitalServiceAPI(
            cinema_id="test_id", account_id="accountid_test", cinema_api_token="token_test", api_url="test_url"
        )

        # When
        try:
            cine_digital_service.cancel_booking(["111111111111", "222222222222", "333333333333"])
        except cds_exceptions.CineDigitalServiceAPIException:
            pytest.fail("Should not raise CineDigitalServiceAPIException")


class CineDigitalServiceGetVoucherForShowTest:
    @patch("pcapi.core.external_bookings.cds.client.get_resource")
    def test_should_return_none_when_show_does_not_have_pass_culture_tariff(self, mocked_get_resource):
        show = cds_serializers.ShowCDS(
            id=1,
            is_cancelled=False,
            is_deleted=False,
            is_disabled_seatmap=True,
            is_empty_seatmap=True,
            remaining_place=88,
            internet_remaining_place=20,
            showtime=datetime.datetime.utcnow(),
            shows_tariff_pos_type_collection=[cds_serializers.ShowTariffCDS(tariff=cds_serializers.IdObjectCDS(id=5))],
            screen=cds_serializers.IdObjectCDS(id=1),
            media=cds_serializers.IdObjectCDS(id=52),
        )
        json_voucher_types = [
            {"id": 1, "code": "TESTCODE", "tariffid": {"id": 2, "price": 5, "active": True, "labeltariff": ""}},
            {"id": 2, "code": "PSCULTURE", "tariffid": {"id": 3, "price": 6, "active": True, "labeltariff": ""}},
        ]

        mocked_get_resource.return_value = json_voucher_types

        cine_digital_service = CineDigitalServiceAPI(
            cinema_id="test_id", account_id="accountid_test", cinema_api_token="token_test", api_url="test_url"
        )

        voucher_type = cine_digital_service.get_voucher_type_for_show(show)

        assert not voucher_type

    @patch("pcapi.core.external_bookings.cds.client.get_resource")
    def test_should_return_psculture_voucher_with_the_lower_price(self, mocked_get_resource):
        show = cds_serializers.ShowCDS(
            id=1,
            is_cancelled=False,
            is_deleted=False,
            is_disabled_seatmap=False,
            is_empty_seatmap=False,
            remaining_place=88,
            internet_remaining_place=20,
            showtime=datetime.datetime.utcnow(),
            shows_tariff_pos_type_collection=[
                cds_serializers.ShowTariffCDS(tariff=cds_serializers.IdObjectCDS(id=3)),
                cds_serializers.ShowTariffCDS(tariff=cds_serializers.IdObjectCDS(id=2)),
            ],
            screen=cds_serializers.IdObjectCDS(id=1),
            media=cds_serializers.IdObjectCDS(id=52),
        )
        json_voucher_types = [
            {"id": 1, "code": "PSCULTURE", "tariffid": {"id": 2, "price": 5, "active": True, "labeltariff": ""}},
            {"id": 2, "code": "PSCULTURE", "tariffid": {"id": 3, "price": 6, "active": True, "labeltariff": ""}},
        ]

        mocked_get_resource.return_value = json_voucher_types

        cine_digital_service = CineDigitalServiceAPI(
            cinema_id="test_id", account_id="accountid_test", cinema_api_token="token_test", api_url="test_url"
        )

        voucher_type = cine_digital_service.get_voucher_type_for_show(show)
        assert voucher_type.id == 1
        assert voucher_type.tariff.id == 2
        assert voucher_type.tariff.price == 5


@pytest.mark.usefixtures("db_session")
class CineDigitalServiceBookTicketTest:
    @patch("pcapi.core.external_bookings.cds.client.post_resource")
    @patch("pcapi.core.external_bookings.cds.client.CineDigitalServiceAPI.get_show")
    @patch("pcapi.core.external_bookings.cds.client.CineDigitalServiceAPI.get_screen")
    @patch("pcapi.core.external_bookings.cds.client.CineDigitalServiceAPI.get_available_seat")
    @patch("pcapi.core.external_bookings.cds.client.CineDigitalServiceAPI.get_pc_voucher_types")
    @patch("pcapi.core.external_bookings.cds.client.CineDigitalServiceAPI.get_voucher_payment_type")
    def test_should_call_connector_with_correct_args_and_return_barcode_and_seat_number(
        self,
        mocked_get_voucher_payment_type,
        mocked_get_pc_voucher_types,
        mocked_get_available_seat,
        mocked_get_screen,
        mocked_get_show,
        mocked_post_resource,
    ):
        beneficiary = users_factories.BeneficiaryGrant18Factory()
        booking = bookings_factories.BookingFactory(user=beneficiary, quantity=1)
        mocked_get_voucher_payment_type.return_value = cds_serializers.PaymentTypeCDS(
            id=12, internal_code="VCH", is_active=True
        )
        mocked_get_pc_voucher_types.return_value = [
            cds_serializers.VoucherTypeCDS(
                id=3,
                code="PSCULTURE",
                tariff=cds_serializers.TariffCDS(id=42, price=5, is_active=True, label="pass Culture"),
            )
        ]

        mocked_get_available_seat.return_value = [
            cds_serializers.SeatCDS(
                (0, 0), create_screen_cds(), cds_serializers.SeatmapCDS(__root__=[[1, 1, 1], [1, 1, 1], [1, 1, 1]])
            ),
        ]

        mocked_get_show.return_value = create_show_cds(
            id_=181,
            shows_tariff_pos_type_ids=[42],
            is_empty_seatmap='["1", "1", "1"], ["1", "1", "1"], ["1", "1", "1"]]',
        )
        mocked_get_screen.return_value = create_screen_cds()

        json_create_transaction = {
            "id": 2964,
            "invoiceid": "3472",
            "tickets": [
                {
                    "barcode": "141414141414",
                    "canceled": False,
                    "cancellable": True,
                    "id": 7699,
                    "seatcol": 1,
                    "seatnumber": "A_1",
                    "seatrow": 1,
                }
            ],
        }

        mocked_post_resource.return_value = json_create_transaction

        cine_digital_service = CineDigitalServiceAPI(
            cinema_id="test_id", account_id="accountid_test", cinema_api_token="token_test", api_url="test_url"
        )

        tickets = cine_digital_service.book_ticket(show_id=14, booking=booking, beneficiary=beneficiary)

        create_transaction_body_arg_call = mocked_post_resource.call_args_list[0][0][4]

        assert create_transaction_body_arg_call.cinema_id == "test_id"
        assert len(create_transaction_body_arg_call.ticket_sale_collection) == 1
        assert create_transaction_body_arg_call.ticket_sale_collection[0].id == -1
        assert create_transaction_body_arg_call.ticket_sale_collection[0].show.id == 181
        assert create_transaction_body_arg_call.ticket_sale_collection[0].tariff.id == 42
        assert create_transaction_body_arg_call.ticket_sale_collection[0].seat_number == "A_1"

        assert len(tickets) == 1
        assert tickets[0].barcode == "141414141414"
        assert tickets[0].seat_number == "A_1"

    @patch("pcapi.core.external_bookings.cds.client.post_resource")
    @patch("pcapi.core.external_bookings.cds.client.CineDigitalServiceAPI.get_show")
    @patch("pcapi.core.external_bookings.cds.client.CineDigitalServiceAPI.get_screen")
    @patch("pcapi.core.external_bookings.cds.client.CineDigitalServiceAPI.get_available_duo_seat")
    @patch("pcapi.core.external_bookings.cds.client.CineDigitalServiceAPI.get_pc_voucher_types")
    @patch("pcapi.core.external_bookings.cds.client.CineDigitalServiceAPI.get_voucher_payment_type")
    def test_should_call_connector_with_correct_args_and_return_barcodes_and_seat_numbers_for_duo(
        self,
        mocked_get_voucher_payment_type,
        mocked_get_pc_voucher_types,
        mocked_get_available_duo_seat,
        mocked_get_screen,
        mocked_get_show,
        mocked_post_resource,
        app,
    ):
        beneficiary = users_factories.BeneficiaryGrant18Factory()
        booking = bookings_factories.BookingFactory(user=beneficiary, quantity=2)
        venue_id = booking.venueId
        mocked_get_voucher_payment_type.return_value = cds_serializers.PaymentTypeCDS(
            id=12, internal_code="VCH", is_active=True
        )
        mocked_get_pc_voucher_types.return_value = [
            cds_serializers.VoucherTypeCDS(
                id=3,
                code="PSCULTURE",
                tariff=cds_serializers.TariffCDS(id=42, price=5, is_active=True, label="pass Culture"),
            )
        ]
        mocked_seatmap = cds_serializers.SeatmapCDS(__root__=[[1, 1, 1], [1, 1, 1], [1, 1, 1]])
        mocked_get_available_duo_seat.return_value = [
            cds_serializers.SeatCDS((0, 0), create_screen_cds(), mocked_seatmap),
            cds_serializers.SeatCDS((0, 1), create_screen_cds(), mocked_seatmap),
        ]

        mocked_get_show.return_value = create_show_cds(
            id_=181,
            shows_tariff_pos_type_ids=[42],
            is_empty_seatmap='["1", "1", "1"], ["1", "1", "1"], ["1", "1", "1"]]',
        )
        mocked_get_screen.return_value = create_screen_cds()

        json_create_transaction = {
            "id": 2964,
            "invoiceid": "3472",
            "tickets": [
                {
                    "barcode": "141414141414",
                    "canceled": False,
                    "cancellable": True,
                    "id": 7699,
                    "seatcol": 1,
                    "seatnumber": "A_1",
                    "seatrow": 1,
                },
                {
                    "barcode": "252525252525",
                    "canceled": False,
                    "cancellable": True,
                    "id": 7700,
                    "seatcol": 1,
                    "seatnumber": "A_2",
                    "seatrow": 2,
                },
            ],
        }

        mocked_post_resource.return_value = json_create_transaction

        cine_digital_service = CineDigitalServiceAPI(
            cinema_id="test_id", account_id="accountid_test", cinema_api_token="token_test", api_url="test_url"
        )

        tickets = cine_digital_service.book_ticket(show_id=14, booking=booking, beneficiary=beneficiary)

        create_transaction_body_arg_call = mocked_post_resource.call_args_list[0][0][4]

        assert create_transaction_body_arg_call.cinema_id == "test_id"
        assert len(create_transaction_body_arg_call.ticket_sale_collection) == 2
        assert create_transaction_body_arg_call.ticket_sale_collection[0].id == -1
        assert create_transaction_body_arg_call.ticket_sale_collection[0].show.id == 181
        assert create_transaction_body_arg_call.ticket_sale_collection[0].tariff.id == 42
        assert create_transaction_body_arg_call.ticket_sale_collection[0].seat_number == "A_1"
        assert create_transaction_body_arg_call.ticket_sale_collection[1].id == -2
        assert create_transaction_body_arg_call.ticket_sale_collection[1].seat_number == "A_2"
        assert len(create_transaction_body_arg_call.payement_collection) == 2
        assert create_transaction_body_arg_call.payement_collection[0].id == -1
        assert create_transaction_body_arg_call.payement_collection[0].amount == 5.0
        assert create_transaction_body_arg_call.payement_collection[0].payement_type.id == 12
        assert create_transaction_body_arg_call.payement_collection[1].id == -2
        assert create_transaction_body_arg_call.payement_collection[1].amount == 5.0
        assert create_transaction_body_arg_call.payement_collection[1].payement_type.id == 12

        assert len(tickets) == 2
        assert tickets[0].barcode == "141414141414"
        assert tickets[0].seat_number == "A_1"
        assert tickets[1].barcode == "252525252525"
        assert tickets[1].seat_number == "A_2"

        redis_external_bookings = app.redis_client.lrange("api:external_bookings:barcodes", 0, -1)
        assert len(redis_external_bookings) == 2
        first_external_booking_info = json.loads(redis_external_bookings[0])
        assert first_external_booking_info["barcode"] == "141414141414"
        assert first_external_booking_info["venue_id"] == venue_id
        assert first_external_booking_info["timestamp"]
        second_external_booking_info = json.loads(redis_external_bookings[1])
        assert second_external_booking_info["barcode"] == "252525252525"
        assert first_external_booking_info["venue_id"] == venue_id
        assert first_external_booking_info["timestamp"]

    @patch("pcapi.core.external_bookings.cds.client.post_resource")
    @patch("pcapi.core.external_bookings.cds.client.CineDigitalServiceAPI.get_show")
    @patch("pcapi.core.external_bookings.cds.client.CineDigitalServiceAPI.get_screen")
    @patch("pcapi.core.external_bookings.cds.client.CineDigitalServiceAPI.get_pc_voucher_types")
    @patch("pcapi.core.external_bookings.cds.client.CineDigitalServiceAPI.get_voucher_payment_type")
    def test_should_call_connector_with_correct_args_and_return_barcode_when_setamap_is_disabled(
        self,
        mocked_get_voucher_payment_type,
        mocked_get_pc_voucher_types,
        mocked_get_screen,
        mocked_get_show,
        mocked_post_resource,
    ):
        beneficiary = users_factories.BeneficiaryGrant18Factory()
        booking = bookings_factories.BookingFactory(user=beneficiary, quantity=1)
        mocked_get_voucher_payment_type.return_value = cds_serializers.PaymentTypeCDS(
            id=12, internal_code="VCH", is_active=True
        )
        mocked_get_pc_voucher_types.return_value = [
            cds_serializers.VoucherTypeCDS(
                id=3,
                code="PSCULTURE",
                tariff=cds_serializers.TariffCDS(id=42, price=5, is_active=True, label="pass Culture"),
            )
        ]

        mocked_get_show.return_value = create_show_cds(
            id_=181, shows_tariff_pos_type_ids=[42], is_disabled_seatmap=True, is_empty_seatmap=True
        )
        mocked_get_screen.return_value = create_screen_cds()

        json_create_transaction = {
            "id": 2964,
            "invoiceid": "3472",
            "tickets": [
                {
                    "barcode": "141414141414",
                    "canceled": False,
                    "cancellable": True,
                    "id": 7699,
                }
            ],
        }

        mocked_post_resource.return_value = json_create_transaction

        cine_digital_service = CineDigitalServiceAPI(
            cinema_id="test_id", account_id="accountid_test", cinema_api_token="token_test", api_url="test_url"
        )

        tickets = cine_digital_service.book_ticket(show_id=14, booking=booking, beneficiary=beneficiary)

        create_transaction_body_arg_call = mocked_post_resource.call_args_list[0][0][4]

        assert create_transaction_body_arg_call.cinema_id == "test_id"
        assert len(create_transaction_body_arg_call.ticket_sale_collection) == 1
        assert create_transaction_body_arg_call.ticket_sale_collection[0].id == -1
        assert create_transaction_body_arg_call.ticket_sale_collection[0].show.id == 181
        assert create_transaction_body_arg_call.ticket_sale_collection[0].tariff.id == 42
        assert not create_transaction_body_arg_call.ticket_sale_collection[0].seat_number

        assert len(tickets) == 1
        assert tickets[0].barcode == "141414141414"
        assert not tickets[0].seat_number


class CineDigitalServiceGetMoviesTest:
    @patch("pcapi.core.external_bookings.cds.client.get_resource")
    def test_should_return_movies_information(self, mocked_get_resource):
        # Given
        token = "token_test"
        api_url = "apiUrl_test/"
        account_id = "accountid_test"
        resource = ResourceCDS.MEDIA

        json_movies = [
            {
                "id": 1,
                "title": "Test movie #1",
                "duration": 7200,
                "storyline": "Test description #1",
                "visanumber": "123",
            },
            {
                "id": 2,
                "title": "Test movie #2",
                "duration": 5400,
                "storyline": "Test description #2",
                "visanumber": "456",
            },
            {
                "id": 2,
                "title": "Test movie #2",
                "duration": 5400,
                "storyline": "Test description #2",
                # No visanumber
            },
        ]

        mocked_get_resource.return_value = json_movies

        # when
        cine_digital_service = CineDigitalServiceAPI(
            cinema_id="cinemaid_test",
            account_id="accountid_test",
            cinema_api_token="token_test",
            api_url="apiUrl_test/",
        )
        movies = cine_digital_service.get_venue_movies()

        # then
        mocked_get_resource.assert_called_once_with(api_url, account_id, token, resource)
        assert len(movies) == 3


class CineDigitalServiceGetHardcodedSeatmapTest:
    @patch("pcapi.core.external_bookings.cds.client.get_resource")
    def test_should_return_hardcoded_seatmap_when_exists(self, mocked_get_resource):
        token = "token_test"
        api_url = "apiUrl_test/"
        account_id = "accountid_test"
        cinema_id = "cinemaid_test"
        show = create_show_cds(screen_id=30)

        mocked_hardcoded_seatmap = '["C_17","C_15",0,"C_13","C_11","C_9"], ["B_17","B_15",0,"B_13","B_11","B_9"], ["A_19","A_17","A_15","A_13","A_11"]]'
        json_cinema_parameters = [
            {
                "internetsalegaugeactive": True,
                "id": cinema_id,
                "cinemaParameters": [
                    {
                        "cinemaid": cinema_id,
                        "id": 1,
                        "key": "SEATMAP_HARDCODED_LABELS_SCREENID_30",
                        "value": mocked_hardcoded_seatmap,
                    }
                ],
            }
        ]
        mocked_get_resource.return_value = json_cinema_parameters

        cine_digital_service = CineDigitalServiceAPI(
            cinema_id=cinema_id,
            account_id=account_id,
            api_url=api_url,
            cinema_api_token=token,
        )

        hardcoded_seatmap = cine_digital_service.get_hardcoded_setmap(show=show)

        assert hardcoded_seatmap == mocked_hardcoded_seatmap

    @patch("pcapi.core.external_bookings.cds.client.get_resource")
    def test_should_return_none_when_hardcoded_seatmap_does_not_exists(self, mocked_get_resource):
        token = "token_test"
        api_url = "apiUrl_test/"
        account_id = "accountid_test"
        cinema_id = "cinemaid_test"
        show = create_show_cds(screen_id=30)

        json_cinema_parameters = [{"internetsalegaugeactive": True, "id": cinema_id, "cinemaParameters": []}]
        mocked_get_resource.return_value = json_cinema_parameters

        cine_digital_service = CineDigitalServiceAPI(
            cinema_id=cinema_id,
            account_id=account_id,
            api_url=api_url,
            cinema_api_token=token,
        )

        hardcoded_seatmap = cine_digital_service.get_hardcoded_setmap(show=show)

        assert not hardcoded_seatmap
