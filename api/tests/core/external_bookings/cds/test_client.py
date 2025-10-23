import copy
import datetime
import json
import logging
from unittest.mock import patch

import pytest
import time_machine

import pcapi.core.bookings.factories as bookings_factories
import pcapi.core.external_bookings.cds.client as cds_client
import pcapi.core.external_bookings.exceptions as external_bookings_exceptions
import pcapi.core.users.factories as users_factories
from pcapi.core.external_bookings.cds import serializers as cds_serializers
from pcapi.core.external_bookings.cds.client import CineDigitalServiceAPI
from pcapi.utils import date as date_utils


def create_show_cds(
    id_: int = 1,
    is_cancelled: bool = False,
    is_deleted: bool = False,
    is_disabled_seatmap: bool = False,
    is_empty_seatmap: str | bool = False,
    remaining_place: int = 88,
    internet_remaining_place: int = 100,
    showtime: datetime.datetime = date_utils.get_naive_utc_now(),
    shows_tariff_pos_type_ids=(),
    screen_id: int = 50,
    media_id: int = 52,
    mediaoptions_ids=(),
) -> cds_serializers.ShowCDS:
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
        shows_mediaoptions_collection=[
            cds_serializers.ShowsMediaoptionsCDS(media_options_id=cds_serializers.IdObjectCDS(id=media_option_id))
            for media_option_id in mediaoptions_ids
        ],
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


MANY_SHOWS_RESPONSE_JSON = [
    {
        "id": 1,
        "remaining_place": 88,
        "internet_remaining_place": 10,
        "disableseatmap": False,
        "is_empty_seatmap": False,
        "showtime": "2022-03-28T12:00:00.000+0200",
        "is_cancelled": False,
        "is_deleted": False,
        "showsTariffPostypeCollection": [
            {"tariffid": {"id": 96}},
            {"tariffid": {"id": 3}},
            {"tariffid": {"id": 2}},
        ],
        "screenid": {"id": 10},
        "mediaid": {"id": 52},
        "showsMediaoptionsCollection": [
            {"mediaoptionsid": {"id": 12}},
        ],
    },
    {
        "id": 2,
        "remaining_place": 88,
        "internet_remaining_place": 30,
        "disableseatmap": False,
        "is_empty_seatmap": False,
        "showtime": "2022-03-29T12:00:00.000+0200",
        "is_cancelled": False,
        "is_deleted": False,
        "showsTariffPostypeCollection": [
            {"tariffid": {"id": 96}},
        ],
        "screenid": {"id": 10},
        "mediaid": {"id": 52},
        "showsMediaoptionsCollection": [
            {"mediaoptionsid": {"id": 12}},
        ],
    },
    {
        "id": 3,
        "remaining_place": 88,
        "internet_remaining_place": 100,
        "disableseatmap": False,
        "is_empty_seatmap": False,
        "showtime": "2022-03-30T12:00:00.000+0200",
        "is_cancelled": False,
        "is_deleted": False,
        "showsTariffPostypeCollection": [{"tariffid": {"id": 96}}],
        "screenid": {"id": 20},
        "mediaid": {"id": 52},
        "showsMediaoptionsCollection": [
            {"mediaoptionsid": {"id": 12}},
        ],
    },
]

ONE_SHOW_RESPONSE_JSON = [
    {
        "id": 1,
        "remaining_place": 88,
        "internet_remaining_place": 10,
        "disableseatmap": False,
        "is_empty_seatmap": False,
        "showtime": "2022-03-28T12:00:00.000+0200",
        "is_cancelled": False,
        "is_deleted": False,
        "showsTariffPostypeCollection": [{"tariffid": {"id": 96}}],
        "screenid": {"id": 10},
        "mediaid": {"id": 52},
        "showsMediaoptionsCollection": [
            {"mediaoptionsid": {"id": 12}},
        ],
    },
]


@pytest.mark.settings(CDS_API_URL="apiUrl_test/")
class CineDigitalServiceGetShowTest:
    def test_should_return_show_corresponding_to_show_id(self, caplog, requests_mock):
        requests_mock.get(
            "https://accountid_test.apiUrl_test/shows?api_token=token_test",
            json=MANY_SHOWS_RESPONSE_JSON,
        )

        cine_digital_service = CineDigitalServiceAPI(
            cinema_id="cinemaid_test",
            account_id="accountid_test",
            cinema_api_token="token_test",
            request_timeout=14,
        )
        with caplog.at_level(logging.DEBUG, logger="pcapi.core.external_bookings.cds.client"):
            show = cine_digital_service.get_show(2)

        assert len(caplog.records) == 1
        assert caplog.records[0].message == "[CINEMA] Call to external API"
        assert caplog.records[0].extra == {
            "api_client": "CineDigitalServiceAPI",
            "method": "GET https://accountid_test.apiUrl_test/shows",
            "cinema_id": "cinemaid_test",
            "response": MANY_SHOWS_RESPONSE_JSON,
        }

        assert show.id == 2

    @pytest.mark.parametrize("response_json", [ONE_SHOW_RESPONSE_JSON, []])
    def test_should_raise_exception_if_show_not_found(self, response_json, requests_mock):
        requests_mock.get(
            "https://accountid_test.apiUrl_test/shows?api_token=token_test",
            json=response_json,
        )
        cine_digital_service = CineDigitalServiceAPI(
            cinema_id="test_id",
            account_id="accountid_test",
            cinema_api_token="token_test",
        )

        with pytest.raises(external_bookings_exceptions.ExternalBookingShowDoesNotExistError):
            cine_digital_service.get_show(4)

    @pytest.mark.parametrize(
        "seatmap, expected_result",
        [("[[]]", True), ("[[1,1,1,1],[2,2,2,2]]", False)],
    )
    def test_should_return_true_if_seatmap_is_empty(self, seatmap, expected_result, requests_mock):
        show = copy.deepcopy(ONE_SHOW_RESPONSE_JSON[0])
        show.update(seatmap=seatmap)
        requests_mock.get("https://account_test.apiUrl_test/shows?api_token=token_test", json=[show])

        cine_digital_service = CineDigitalServiceAPI(
            cinema_id="test_id", account_id="account_test", cinema_api_token="token_test"
        )

        show = cine_digital_service.get_show(1)
        assert show.is_empty_seatmap is expected_result


@pytest.mark.settings(CDS_API_URL="apiUrl_test/")
class CineDigitalServiceGetPaymentTypeTest:
    def test_should_return_voucher_payment_type(self, caplog, requests_mock):
        requests_mock.get(
            "https://accountid_test.apiUrl_test/paiementtype?api_token=token_test",
            json=[
                {"id": 21, "active": True, "internalcode": "VCH"},
                {"id": 22, "active": True, "internalcode": "OTHERPAYMENTYPE"},
            ],
        )

        cine_digital_service = CineDigitalServiceAPI(
            cinema_id="cinemaid_test",
            account_id="accountid_test",
            cinema_api_token="token_test",
        )

        payment_type = cine_digital_service.get_voucher_payment_type()

        with caplog.at_level(logging.DEBUG, logger="pcapi.core.external_bookings.cds.client"):
            payment_type = cine_digital_service.get_voucher_payment_type()

        assert len(caplog.records) == 1
        assert caplog.records[0].message == "[CINEMA] Call to external API"
        assert caplog.records[0].extra == {
            "api_client": "CineDigitalServiceAPI",
            "method": "GET https://accountid_test.apiUrl_test/paiementtype",
            "cinema_id": "cinemaid_test",
            "response": [
                {"id": 21, "active": True, "internalcode": "VCH"},
                {"id": 22, "active": True, "internalcode": "OTHERPAYMENTYPE"},
            ],
        }

        assert payment_type.id == 21
        assert payment_type.internal_code == "VCH"

    def test_should_raise_exception_if_payment_type_not_found(self, requests_mock):
        requests_mock.get(
            "https://accountid_test.apiUrl_test/paiementtype?api_token=token_test",
            json=[
                {"id": 23, "active": True, "internalcode": "OTHERPAYMENTYPE2"},
                {"id": 22, "active": True, "internalcode": "OTHERPAYMENTYPE"},
            ],
        )

        cine_digital_service = CineDigitalServiceAPI(
            cinema_id="test_id", account_id="accountid_test", cinema_api_token="token_test"
        )
        with pytest.raises(cds_client.CineDigitalServiceAPIException) as cds_exception:
            cine_digital_service.get_voucher_payment_type()
        assert (
            str(cds_exception.value)
            == "Pass Culture payment type not found in Cine Digital Service API for cinemaId=test_id & url=https://accountid_test.apiUrl_test/"
        )


@pytest.mark.settings(CDS_API_URL="apiUrl_test/")
class CineDigitalServiceGetPCVoucherTypesTest:
    def test_should_return_only_voucher_types_with_pass_culture_code_and_tariff(self, requests_mock, caplog):
        requests_mock.get(
            "https://accountid_test.apiUrl_test/vouchertype?api_token=token_test",
            json=[
                {"id": 1, "code": "TESTCODE", "tariffid": {"id": 2, "price": 5, "active": True, "labeltariff": ""}},
                {"id": 2, "code": "PSCULTURE", "tariffid": {"id": 3, "price": 5, "active": True, "labeltariff": ""}},
                {"id": 3, "code": "PSCULTURE", "tariffid": {"id": 4, "price": 6, "active": True, "labeltariff": ""}},
                {"id": 4, "code": "PSCULTURE"},
                {"id": 5, "code": None},
            ],
        )
        cine_digital_service = CineDigitalServiceAPI(
            cinema_id="cinemaid_test",
            account_id="accountid_test",
            cinema_api_token="token_test",
        )

        with caplog.at_level(logging.DEBUG, logger="pcapi.core.external_bookings.cds.client"):
            pc_voucher_types = cine_digital_service.get_pc_voucher_types()

        assert len(caplog.records) == 1
        assert caplog.records[0].message == "[CINEMA] Call to external API"
        assert caplog.records[0].extra == {
            "api_client": "CineDigitalServiceAPI",
            "method": "GET https://accountid_test.apiUrl_test/vouchertype",
            "cinema_id": "cinemaid_test",
            "response": [
                {
                    "id": 1,
                    "code": "TESTCODE",
                    "tariffid": {"id": 2, "price": 5, "active": True, "labeltariff": ""},
                },
                {
                    "id": 2,
                    "code": "PSCULTURE",
                    "tariffid": {"id": 3, "price": 5, "active": True, "labeltariff": ""},
                },
                {
                    "id": 3,
                    "code": "PSCULTURE",
                    "tariffid": {"id": 4, "price": 6, "active": True, "labeltariff": ""},
                },
                {"id": 4, "code": "PSCULTURE"},
                {"id": 5, "code": None},
            ],
        }

        assert len(pc_voucher_types) == 2
        assert pc_voucher_types[0].id == 2
        assert pc_voucher_types[0].code == "PSCULTURE"
        assert pc_voucher_types[0].tariff.id == 3
        assert pc_voucher_types[0].tariff.price == 5
        assert pc_voucher_types[1].id == 3
        assert pc_voucher_types[1].tariff.id == 4


@pytest.mark.settings(CDS_API_URL="apiUrl_test/")
class CineDigitalServiceGetScreenTest:
    def test_should_return_screen_corresponding_to_screen_id(self, requests_mock):
        requests_mock.get(
            "https://accountid_test.apiUrl_test/screens?api_token=token_test",
            json=[
                {"id": 1, "seatmapfronttoback": True, "seatmaplefttoright": False, "seatmapskipmissingseats": False},
                {"id": 2, "seatmapfronttoback": False, "seatmaplefttoright": True, "seatmapskipmissingseats": True},
                {"id": 3, "seatmapfronttoback": True, "seatmaplefttoright": True, "seatmapskipmissingseats": True},
            ],
        )
        cine_digital_service = CineDigitalServiceAPI(
            cinema_id="test_id", account_id="accountid_test", cinema_api_token="token_test"
        )
        show = cine_digital_service.get_screen(2)

        assert show.id == 2

    def test_should_raise_exception_if_screen_not_found(self, requests_mock):
        requests_mock.get(
            "https://accountid_test.apiUrl_test/screens?api_token=token_test",
            json=[
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
            ],
        )
        cine_digital_service = CineDigitalServiceAPI(
            cinema_id="test_id", account_id="accountid_test", cinema_api_token="token_test"
        )
        with pytest.raises(cds_client.CineDigitalServiceAPIException) as cds_exception:
            cine_digital_service.get_screen(4)
        assert (
            str(cds_exception.value)
            == "Screen #4 not found in Cine Digital Service API for cinemaId=test_id & url=https://accountid_test.apiUrl_test/"
        )


@pytest.mark.settings(CDS_API_URL="apiUrl_test/")
class CineDigitalServiceGetAvailableSingleSeatTest:
    @patch("pcapi.core.external_bookings.cds.client.CineDigitalServiceAPI.get_hardcoded_seatmap", return_value=[])
    def test_should_return_seat_available(self, mocked_get_hardcoded_seatmap, requests_mock):
        screen = cds_serializers.ScreenCDS(
            id=1,
            seatmapfronttoback=True,
            seatmaplefttoright=True,
            seatmapskipmissingseats=False,
        )

        show = create_show_cds(id_=1)

        requests_mock.get(
            "https://accountid_test.apiUrl_test/shows/1/seatmap?api_token=token_test",
            json=[
                [1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1],
                [1, 3, 1, 1, 1, 1, 1, 1, 0, 1, 1],
                [1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1],
                [1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1],
                [1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1],
                [1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1],
                [1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1],
                [1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1],
                [0, 0, 0, 1, 1, 1, 1, 1, 0, 1, 1],
            ],
        )

        cine_digital_service = CineDigitalServiceAPI(
            cinema_id="test_id", account_id="accountid_test", cinema_api_token="token_test"
        )

        best_seat = cine_digital_service.get_available_seat(show, screen)
        assert len(best_seat) == 1
        assert best_seat[0].seatRow == 4
        assert best_seat[0].seatCol == 5
        assert best_seat[0].seatNumber == "E_6"

    @patch("pcapi.core.external_bookings.cds.client.CineDigitalServiceAPI.get_hardcoded_seatmap")
    def test_should_return_seat_available_when_seatmap_is_hardcoded(self, mocked_get_hardcoded_seatmap, requests_mock):
        mocked_hardcoded_seatmap = [
            ["P_17", "P_15", "P_13", "P_11", "P_9", "P_7", "P_5", "P_3", "P_1"],
            ["M_17", "M_15", "M_13", "M_11", "M_9", "M_7", "M_5", "M_3", "M_1"],
            ["O_17", "O_15", "O_13", "O_11", "O_9", "O_7", "O_5", "O_3", "O_1"],
        ]

        mocked_get_hardcoded_seatmap.return_value = mocked_hardcoded_seatmap

        screen = cds_serializers.ScreenCDS(
            id=1,
            seatmapfronttoback=True,
            seatmaplefttoright=True,
            seatmapskipmissingseats=False,
        )

        show = create_show_cds(id_=1)

        requests_mock.get(
            "https://accountid_test.apiUrl_test/shows/1/seatmap?api_token=token_test",
            json=[
                [1, 1, 1, 1, 1, 1, 0, 1, 1],
                [1, 1, 1, 1, 1, 1, 0, 1, 1],
                [1, 1, 1, 1, 1, 1, 0, 1, 1],
            ],
        )
        cine_digital_service = CineDigitalServiceAPI(
            cinema_id="test_id", account_id="accountid_test", cinema_api_token="token_test"
        )

        best_seat = cine_digital_service.get_available_seat(show, screen)
        assert len(best_seat) == 1
        assert best_seat[0].seatRow == 1
        assert best_seat[0].seatCol == 4
        assert best_seat[0].seatNumber == "M_9"

    @patch("pcapi.core.external_bookings.cds.client.CineDigitalServiceAPI.get_hardcoded_seatmap", return_value=[])
    def test_should_not_return_prm_seat(self, mocked_get_hardcoded_seatmap, requests_mock):
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
        requests_mock.get(
            "https://accountid_test.apiUrl_test/shows/1/seatmap?api_token=token_test",
            json=seatmap_json,
        )
        cine_digital_service = CineDigitalServiceAPI(
            cinema_id="test_id", account_id="accountid_test", cinema_api_token="token_test"
        )
        best_seat = cine_digital_service.get_available_seat(show, screen)
        assert len(best_seat) == 1
        assert best_seat[0].seatRow == 3
        assert best_seat[0].seatCol == 5
        assert best_seat[0].seatNumber == "D_6"

    @patch("pcapi.core.external_bookings.cds.client.CineDigitalServiceAPI.get_hardcoded_seatmap", return_value=[])
    def test_should_return_seat_infos_according_to_screen(self, mocked_get_hardcoded_seatmap, requests_mock):
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

        requests_mock.get(
            "https://accountid_test.apiUrl_test/shows/1/seatmap?api_token=token_test",
            json=seatmap_json,
        )
        cine_digital_service = CineDigitalServiceAPI(
            cinema_id="test_id", account_id="accountid_test", cinema_api_token="token_test"
        )
        best_seat = cine_digital_service.get_available_seat(show, screen)
        assert len(best_seat) == 1
        assert best_seat[0].seatRow == 3
        assert best_seat[0].seatCol == 3
        assert best_seat[0].seatNumber == "B_3"

    def test_should_return_None_if_no_seat_available(self, requests_mock):
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

        requests_mock.get(
            "https://accountid_test.apiUrl_test/shows/1/seatmap?api_token=token_test",
            json=seatmap_json,
        )
        cine_digital_service = CineDigitalServiceAPI(
            cinema_id="test_id", account_id="accountid_test", cinema_api_token="token_test"
        )
        best_seat = cine_digital_service.get_available_seat(show, screen)
        assert not best_seat

    @patch("pcapi.core.external_bookings.cds.client.CineDigitalServiceAPI.get_hardcoded_seatmap", return_value=[])
    def test_should_return_correct_seat_number(self, mocked_get_hardcoded_seatmap, requests_mock):
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

        requests_mock.get(
            "https://accountid_test.apiUrl_test/shows/1/seatmap?api_token=token_test",
            json=seatmap_json,
        )
        cine_digital_service = CineDigitalServiceAPI(
            cinema_id="test_id", account_id="accountid_test", cinema_api_token="token_test"
        )
        best_seat = cine_digital_service.get_available_seat(show, screen)
        assert best_seat[0].seatRow == 5
        assert best_seat[0].seatCol == 18
        assert best_seat[0].seatNumber == "E_16"


@pytest.mark.settings(CDS_API_URL="apiUrl_test/")
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
            cinema_id="test_id", account_id="accountid_test", cinema_api_token="token_test"
        )
        duo_seats = cine_digital_service.get_available_duo_seat(show, screen)
        assert len(duo_seats) == 2
        assert duo_seats[0].seatNumber == "B_2"
        assert duo_seats[1].seatNumber == "B_3"

    @patch("pcapi.core.external_bookings.cds.client.CineDigitalServiceAPI.get_hardcoded_seatmap")
    @patch("pcapi.core.external_bookings.cds.client.CineDigitalServiceAPI.get_seatmap")
    def test_should_return_duo_seat_if_available_when_seatmap_is_hardcoded(
        self, mocked_get_seatmap, mocked_get_hardcoded_seatmap
    ):
        seatmap = cds_serializers.SeatmapCDS(
            __root__=[
                [1, 1, 1, 1, 0, 1],
                [1, 1, 1, 3, 0, 1],
            ]
        )
        mocked_hardcoded_seatmap = [
            ["P_17", "P_15", "P_13", "P_11", "P_9", "P_7"],
            ["M_17", "M_15", "M_13", "M_11", "M_9", "M_7"],
        ]
        screen = cds_serializers.ScreenCDS(
            id=1,
            seatmapfronttoback=True,
            seatmaplefttoright=True,
            seatmapskipmissingseats=False,
        )
        show = create_show_cds(id_=1, screen_id=1)

        mocked_get_seatmap.return_value = seatmap
        mocked_get_hardcoded_seatmap.return_value = mocked_hardcoded_seatmap
        cine_digital_service = CineDigitalServiceAPI(
            cinema_id="test_id", account_id="accountid_test", cinema_api_token="token_test"
        )
        duo_seats = cine_digital_service.get_available_duo_seat(show, screen)
        assert len(duo_seats) == 2
        assert duo_seats[0].seatNumber == "P_13"
        assert duo_seats[1].seatNumber == "P_11"

    def test_should_return_empty_if_less_than_two_seats_available(self, requests_mock):
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

        requests_mock.get(
            "https://accountid_test.apiUrl_test/shows/1/seatmap?api_token=token_test",
            json=seatmap_json,
        )
        cine_digital_service = CineDigitalServiceAPI(
            cinema_id="test_id", account_id="accountid_test", cinema_api_token="token_test"
        )
        duo_seats = cine_digital_service.get_available_duo_seat(show, screen)
        assert len(duo_seats) == 0

    @pytest.mark.settings(CDS_API_URL="apiUrl_test/")
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
            cinema_id="test_id", account_id="accountid_test", cinema_api_token="token_test"
        )
        duo_seats = cine_digital_service.get_available_duo_seat(show, screen)
        assert len(duo_seats) == 2
        assert duo_seats[0].seatNumber == "C_3"
        assert duo_seats[1].seatNumber == "D_3"


@pytest.mark.settings(CDS_API_URL="apiUrl_test/")
class CineDigitalServiceCancelBookingTest:
    def test_should_cancel_booking_with_success(self, requests_mock):
        requests_mock.put(
            "https://accountid_test.apiUrl_test/transaction/cancel?api_token=token_test",
            headers={"Content-Type": "application/json"},
            json={},
        )
        requests_mock.get(
            "https://accountid_test.apiUrl_test/paiementtype?api_token=token_test",
            json=[{"id": 12, "active": True, "internalcode": "VCH"}],
        )
        cine_digital_service = CineDigitalServiceAPI(
            cinema_id="test_id",
            account_id="accountid_test",
            cinema_api_token="token_test",
            request_timeout=12,
        )

        cine_digital_service.cancel_booking(["3107362853729", "1312079646868"])

    def test_should_cancel_booking_with_errors_for_each_barcode(self, requests_mock):
        requests_mock.put(
            "https://accountid_test.apiUrl_test/transaction/cancel?api_token=token_test",
            json={
                "111111111111": "BARCODE_NOT_FOUND",
                "222222222222": "TICKET_ALREADY_CANCELED",
                "333333333333": "AFTER_END_OF_DAY",
                "444444444444": "AFTER_END_OF_SHOW",
                "555555555555": "DAY_CLOSED",
            },
            headers={"Content-Type": "application/json"},
        )
        requests_mock.get(
            "https://accountid_test.apiUrl_test/paiementtype?api_token=token_test",
            json=[{"id": 12, "active": True, "internalcode": "VCH"}],
        )

        cine_digital_service = CineDigitalServiceAPI(
            cinema_id="test_id",
            account_id="accountid_test",
            cinema_api_token="token_test",
        )

        with pytest.raises(cds_client.CineDigitalServiceAPIException) as exception:
            cine_digital_service.cancel_booking(
                ["111111111111", "222222222222", "333333333333", "444444444444", "555555555555"]
            )
        sep = "\n"
        assert (
            str(exception.value)
            == f"""Error while canceling bookings :{sep}111111111111 : BARCODE_NOT_FOUND{sep}222222222222 : TICKET_ALREADY_CANCELED{sep}333333333333 : AFTER_END_OF_DAY{sep}444444444444 : AFTER_END_OF_SHOW{sep}555555555555 : DAY_CLOSED"""
        )

    def test_should_not_raise_error_when_cancel_bookings_already_cancelled(self, requests_mock):
        requests_mock.put(
            "https://accountid_test.apiUrl_test/transaction/cancel?api_token=token_test",
            json={
                "111111111111": "TICKET_ALREADY_CANCELED",
                "222222222222": "TICKET_ALREADY_CANCELED",
                "333333333333": "TICKET_ALREADY_CANCELED",
            },
            headers={"Content-Type": "application/json"},
        )
        requests_mock.get(
            "https://accountid_test.apiUrl_test/paiementtype?api_token=token_test",
            json=[{"id": 12, "active": True, "internalcode": "VCH"}],
        )
        cine_digital_service = CineDigitalServiceAPI(
            cinema_id="test_id", account_id="accountid_test", cinema_api_token="token_test"
        )

        cine_digital_service.cancel_booking(["111111111111", "222222222222", "333333333333"])


@pytest.mark.settings(CDS_API_URL="apiUrl_test/")
class CineDigitalServiceGetVoucherForShowTest:
    def test_should_return_none_when_show_does_not_have_pass_culture_tariff(self, requests_mock):
        show = cds_serializers.ShowCDS(
            id=1,
            is_cancelled=False,
            is_deleted=False,
            is_disabled_seatmap=True,
            is_empty_seatmap=True,
            remaining_place=88,
            internet_remaining_place=20,
            showtime=date_utils.get_naive_utc_now(),
            shows_tariff_pos_type_collection=[cds_serializers.ShowTariffCDS(tariff=cds_serializers.IdObjectCDS(id=5))],
            screen=cds_serializers.IdObjectCDS(id=1),
            media=cds_serializers.IdObjectCDS(id=52),
            shows_mediaoptions_collection=[
                cds_serializers.ShowsMediaoptionsCDS(media_options_id=cds_serializers.IdObjectCDS(id=12))
            ],
        )

        requests_mock.get(
            "https://accountid_test.apiUrl_test/vouchertype?api_token=token_test",
            json=[
                {"id": 1, "code": "TESTCODE", "tariffid": {"id": 2, "price": 5, "active": True, "labeltariff": ""}},
                {"id": 2, "code": "PSCULTURE", "tariffid": {"id": 3, "price": 6, "active": True, "labeltariff": ""}},
            ],
        )

        cine_digital_service = CineDigitalServiceAPI(
            cinema_id="test_id", account_id="accountid_test", cinema_api_token="token_test"
        )

        voucher_type = cine_digital_service.get_voucher_type_for_show(show)

        assert not voucher_type

    def test_should_return_psculture_voucher_with_the_lower_price(self, requests_mock):
        show = cds_serializers.ShowCDS(
            id=1,
            is_cancelled=False,
            is_deleted=False,
            is_disabled_seatmap=False,
            is_empty_seatmap=False,
            remaining_place=88,
            internet_remaining_place=20,
            showtime=date_utils.get_naive_utc_now(),
            shows_tariff_pos_type_collection=[
                cds_serializers.ShowTariffCDS(tariff=cds_serializers.IdObjectCDS(id=3)),
                cds_serializers.ShowTariffCDS(tariff=cds_serializers.IdObjectCDS(id=2)),
            ],
            screen=cds_serializers.IdObjectCDS(id=1),
            media=cds_serializers.IdObjectCDS(id=52),
            shows_mediaoptions_collection=[
                cds_serializers.ShowsMediaoptionsCDS(media_options_id=cds_serializers.IdObjectCDS(id=12))
            ],
        )

        requests_mock.get(
            "https://accountid_test.apiUrl_test/vouchertype?api_token=token_test",
            json=[
                {"id": 1, "code": "PSCULTURE", "tariffid": {"id": 2, "price": 5, "active": True, "labeltariff": ""}},
                {"id": 2, "code": "PSCULTURE", "tariffid": {"id": 3, "price": 6, "active": True, "labeltariff": ""}},
            ],
        )

        cine_digital_service = CineDigitalServiceAPI(
            cinema_id="test_id", account_id="accountid_test", cinema_api_token="token_test"
        )

        voucher_type = cine_digital_service.get_voucher_type_for_show(show)
        assert voucher_type.id == 1
        assert voucher_type.tariff.id == 2
        assert voucher_type.tariff.price == 5


@pytest.mark.usefixtures("db_session")
@pytest.mark.settings(CDS_API_URL="apiUrl_test/")
class CineDigitalServiceBookTicketTest:
    @time_machine.travel("2025-09-22T09:23:40.464832", tick=False)
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
        requests_mock,
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
                (0, 0),
                create_screen_cds(),
                seat_map=cds_serializers.SeatmapCDS(__root__=[[1, 1, 1], [1, 1, 1], [1, 1, 1]]),
                hardcoded_seatmap=[],
            ),
        ]

        mocked_get_show.return_value = create_show_cds(
            id_=181,
            shows_tariff_pos_type_ids=[42],
            is_empty_seatmap='["1", "1", "1"], ["1", "1", "1"], ["1", "1", "1"]]',
        )
        mocked_get_screen.return_value = create_screen_cds()

        requests_mock.post(
            "https://accountid_test.apiUrl_test/transaction/create?api_token=token_test",
            json={
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
            },
        )

        cine_digital_service = CineDigitalServiceAPI(
            cinema_id="test_id",
            account_id="accountid_test",
            cinema_api_token="token_test",
            request_timeout=12,
        )

        tickets = cine_digital_service.book_ticket(show_id=14, booking=booking, beneficiary=beneficiary)

        post_request = requests_mock.last_request
        assert post_request.method == "POST"
        assert post_request.url == "https://accountid_test.apiurl_test/transaction/create?api_token=token_test"
        assert post_request.json() == {
            "canceled": False,
            "cinemaid": "test_id",
            "paiementCollection": [
                {"amount": 5.0, "id": -1, "paiementtypeid": {"id": 12}, "vouchertypeid": {"id": 3}},
            ],
            "ticketsaleCollection": [
                {
                    "canceled": False,
                    "cinemaid": "test_id",
                    "disabledperson": False,
                    "id": -1,
                    "operationdate": "2025-09-22T09:23:40.464832",
                    "seatcol": 0,
                    "seatnumber": "A_1",
                    "seatrow": 0,
                    "showid": {"id": 181},
                    "tariffid": {"id": 42},
                    "vouchertype": "PSCULTURE",
                },
            ],
            "transactiondate": "2025-09-22T09:23:40.464832",
        }

        assert len(tickets) == 1
        assert tickets[0].barcode == "141414141414"
        assert tickets[0].seat_number == "A_1"

    @time_machine.travel("2025-09-22T09:23:40.464832", tick=False)
    @patch("pcapi.core.external_bookings.cds.client.CineDigitalServiceAPI.get_available_seat")
    @patch("pcapi.core.external_bookings.cds.client.CineDigitalServiceAPI.get_show")
    @patch("pcapi.core.external_bookings.cds.client.CineDigitalServiceAPI.get_screen")
    @patch("pcapi.core.external_bookings.cds.client.CineDigitalServiceAPI.get_available_duo_seat")
    @patch("pcapi.core.external_bookings.cds.client.CineDigitalServiceAPI.get_pc_voucher_types")
    @patch("pcapi.core.external_bookings.cds.client.CineDigitalServiceAPI.get_voucher_payment_type")
    @pytest.mark.parametrize("booking_quantity", [0, 1])
    def test_should_raise_not_enough_seats_error(
        self,
        mocked_get_voucher_payment_type,
        mocked_get_pc_voucher_types,
        mocked_get_available_duo_seat,
        mocked_get_screen,
        mocked_get_show,
        mocked_get_available_seat,
        booking_quantity,
    ):
        beneficiary = users_factories.BeneficiaryGrant18Factory()
        booking = bookings_factories.BookingFactory(user=beneficiary, quantity=booking_quantity)

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

        mocked_get_available_seat.return_value = []
        mocked_get_available_duo_seat.return_value = []

        mocked_get_show.return_value = create_show_cds(
            id_=181,
            shows_tariff_pos_type_ids=[42],
            is_empty_seatmap='["0", "0", "0"], ["0", "0", "0"], ["0", "0", "0"]]',
        )
        mocked_get_screen.return_value = create_screen_cds()

        cine_digital_service = CineDigitalServiceAPI(
            cinema_id="test_id", account_id="accountid_test", cinema_api_token="token_test"
        )
        with pytest.raises(external_bookings_exceptions.ExternalBookingNotEnoughSeatsError) as exc:
            cine_digital_service.book_ticket(show_id=14, booking=booking, beneficiary=beneficiary)

        assert exc.value.remainingQuantity == 0

    @time_machine.travel("2025-09-22T09:23:40.464832", tick=False)
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
        requests_mock,
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
            cds_serializers.SeatCDS((0, 0), create_screen_cds(), mocked_seatmap, hardcoded_seatmap=[]),
            cds_serializers.SeatCDS((0, 1), create_screen_cds(), mocked_seatmap, hardcoded_seatmap=[]),
        ]

        mocked_get_show.return_value = create_show_cds(
            id_=181,
            shows_tariff_pos_type_ids=[42],
            is_empty_seatmap='["1", "1", "1"], ["1", "1", "1"], ["1", "1", "1"]]',
        )
        mocked_get_screen.return_value = create_screen_cds()

        requests_mock.post(
            "https://accountid_test.apiUrl_test/transaction/create?api_token=token_test",
            json={
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
            },
        )

        cine_digital_service = CineDigitalServiceAPI(
            cinema_id="test_id", account_id="accountid_test", cinema_api_token="token_test"
        )

        tickets = cine_digital_service.book_ticket(show_id=14, booking=booking, beneficiary=beneficiary)

        post_request = requests_mock.last_request
        assert post_request.method == "POST"
        assert post_request.url == "https://accountid_test.apiurl_test/transaction/create?api_token=token_test"
        assert post_request.json() == {
            "canceled": False,
            "cinemaid": "test_id",
            "paiementCollection": [
                {"amount": 5.0, "id": -1, "paiementtypeid": {"id": 12}, "vouchertypeid": {"id": 3}},
                {"amount": 5.0, "id": -2, "paiementtypeid": {"id": 12}, "vouchertypeid": {"id": 3}},
            ],
            "ticketsaleCollection": [
                {
                    "canceled": False,
                    "cinemaid": "test_id",
                    "disabledperson": False,
                    "id": -1,
                    "operationdate": "2025-09-22T09:23:40.464832",
                    "seatcol": 0,
                    "seatnumber": "A_1",
                    "seatrow": 0,
                    "showid": {"id": 181},
                    "tariffid": {"id": 42},
                    "vouchertype": "PSCULTURE",
                },
                {
                    "canceled": False,
                    "cinemaid": "test_id",
                    "disabledperson": False,
                    "id": -2,
                    "operationdate": "2025-09-22T09:23:40.464832",
                    "seatcol": 1,
                    "seatnumber": "A_2",
                    "seatrow": 0,
                    "showid": {"id": 181},
                    "tariffid": {"id": 42},
                    "vouchertype": "PSCULTURE",
                },
            ],
            "transactiondate": "2025-09-22T09:23:40.464832",
        }

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

    @time_machine.travel("2025-09-22T09:23:40.464832", tick=False)
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
        requests_mock,
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

        requests_mock.post(
            "https://accountid_test.apiUrl_test/transaction/create?api_token=token_test",
            json={
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
            },
        )

        cine_digital_service = CineDigitalServiceAPI(
            cinema_id="test_id", account_id="accountid_test", cinema_api_token="token_test"
        )

        tickets = cine_digital_service.book_ticket(show_id=14, booking=booking, beneficiary=beneficiary)

        post_request = requests_mock.last_request
        assert post_request.method == "POST"
        assert post_request.url == "https://accountid_test.apiurl_test/transaction/create?api_token=token_test"
        assert post_request.json() == {
            "canceled": False,
            "cinemaid": "test_id",
            "paiementCollection": [
                {"amount": 5.0, "id": -1, "paiementtypeid": {"id": 12}, "vouchertypeid": {"id": 3}},
            ],
            "ticketsaleCollection": [
                {
                    "canceled": False,
                    "cinemaid": "test_id",
                    "disabledperson": False,
                    "id": -1,
                    "operationdate": "2025-09-22T09:23:40.464832",
                    "seatcol": None,
                    "seatnumber": None,
                    "seatrow": None,
                    "showid": {"id": 181},
                    "tariffid": {"id": 42},
                    "vouchertype": "PSCULTURE",
                },
            ],
            "transactiondate": "2025-09-22T09:23:40.464832",
        }

        assert len(tickets) == 1
        assert tickets[0].barcode == "141414141414"
        assert not tickets[0].seat_number


@pytest.mark.settings(CDS_API_URL="apiUrl_test/")
class CineDigitalServiceGetMoviesTest:
    def test_should_return_movies_information(self, requests_mock):
        requests_mock.get(
            "https://accountid_test.apiUrl_test/media?api_token=token_test",
            json=[
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
            ],
        )

        cine_digital_service = CineDigitalServiceAPI(
            cinema_id="cinemaid_test",
            account_id="accountid_test",
            cinema_api_token="token_test",
        )
        movies = cine_digital_service.get_venue_movies()

        assert len(movies) == 3


@pytest.mark.settings(CDS_API_URL="apiUrl_test/")
class CineDigitalServiceGetHardcodedSeatmapTest:
    def test_should_return_hardcoded_seatmap_when_exists(self, requests_mock):
        show = create_show_cds(screen_id=30)

        expected_hardcoded_seatmap = [
            ["C_17", "C_15", 0, "C_13", "C_11", "C_9"],
            ["B_17", "B_15", 0, "B_13", "B_11", "B_9"],
            ["A_19", "A_17", "A_15", "A_13", "A_11"],
        ]
        requests_mock.get(
            "https://accountid_test.apiUrl_test/cinemas?api_token=token_test",
            json=[
                {
                    "internetsalegaugeactive": True,
                    "id": "cinemaid_test",
                    "cinemaParameters": [
                        {
                            "cinemaid": "cinemaid_test",
                            "key": "SEATMAP_HARDCODED_LABELS_SCREENID_30",
                            "id": 1,
                            "value": json.dumps(expected_hardcoded_seatmap),
                        }
                    ],
                }
            ],
        )

        cine_digital_service = CineDigitalServiceAPI(
            cinema_id="cinemaid_test",
            account_id="accountid_test",
            cinema_api_token="token_test",
        )

        hardcoded_seatmap = cine_digital_service.get_hardcoded_seatmap(show=show)

        assert hardcoded_seatmap == expected_hardcoded_seatmap

    def test_should_return_none_when_hardcoded_seatmap_does_not_exist(self, requests_mock):
        cinema_id = "cinemaid_test"
        show = create_show_cds(screen_id=30)

        requests_mock.get(
            "https://accountid_test.apiUrl_test/cinemas?api_token=token_test",
            json=[{"internetsalegaugeactive": True, "id": cinema_id, "cinemaParameters": []}],
        )

        cine_digital_service = CineDigitalServiceAPI(
            cinema_id="cinemaid_test",
            account_id="accountid_test",
            cinema_api_token="token_test",
        )

        hardcoded_seatmap = cine_digital_service.get_hardcoded_seatmap(show=show)

        assert not hardcoded_seatmap
