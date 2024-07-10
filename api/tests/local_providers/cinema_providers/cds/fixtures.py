from datetime import datetime

from pcapi.connectors.serialization.cine_digital_service_serializers import IdObjectCDS
from pcapi.connectors.serialization.cine_digital_service_serializers import MediaCDS
from pcapi.connectors.serialization.cine_digital_service_serializers import ShowCDS
from pcapi.connectors.serialization.cine_digital_service_serializers import ShowTariffCDS
from pcapi.connectors.serialization.cine_digital_service_serializers import ShowsMediaoptionsCDS


MOVIE_1 = MediaCDS(
    id=123,
    title="Coupez !",
    duration=7200,
    storyline="Ca tourne mal",
    posterpath="https://example.com/coupez.png",
    visanumber="123456",
    allocineid="291483",
)

MOVIE_2 = MediaCDS(
    id=51,
    title="Top Gun",
    duration=9000,
    storyline="Film sur les avions",
    posterpath="https://example.com/topgun.png",
    visanumber="333333",
    allocineid="2133",
)

MOVIE_1_SHOW_1 = ShowCDS(
    id=1,
    is_cancelled=False,
    is_deleted=False,
    is_disabled_seatmap=False,
    is_empty_seatmap=False,
    remaining_place=77,
    internet_remaining_place=10,
    showtime=datetime(2022, 6, 20, 11, 00, 00),
    shows_tariff_pos_type_collection=[ShowTariffCDS(tariff=IdObjectCDS(id=4))],
    screen=IdObjectCDS(id=1),
    media=IdObjectCDS(id=123),
    showsMediaoptionsCollection=[ShowsMediaoptionsCDS(mediaoptionsid=IdObjectCDS(id=5))],
)

MOVIE_1_SHOW_1_SOLD_OUT = ShowCDS(
    id=1,
    is_cancelled=False,
    is_deleted=False,
    is_disabled_seatmap=False,
    is_empty_seatmap=False,
    remaining_place=77,
    internet_remaining_place=0,
    showtime=datetime(2022, 6, 20, 11, 00, 00),
    shows_tariff_pos_type_collection=[ShowTariffCDS(tariff=IdObjectCDS(id=4))],
    screen=IdObjectCDS(id=1),
    media=IdObjectCDS(id=123),
    showsMediaoptionsCollection=[ShowsMediaoptionsCDS(mediaoptionsid=IdObjectCDS(id=5))],
)

MOVIE_2_SHOW_1 = ShowCDS(
    id=2,
    is_cancelled=False,
    is_deleted=False,
    is_disabled_seatmap=False,
    is_empty_seatmap=False,
    remaining_place=78,
    internet_remaining_place=10,
    showtime=datetime(2022, 7, 1, 12, 00, 00),
    shows_tariff_pos_type_collection=[ShowTariffCDS(tariff=IdObjectCDS(id=4))],
    screen=IdObjectCDS(id=1),
    media=IdObjectCDS(id=51),
    showsMediaoptionsCollection=[ShowsMediaoptionsCDS(mediaoptionsid=IdObjectCDS(id=5))],
)

MOVIE_1_SHOW_2 = ShowCDS(
    id=3,
    is_cancelled=False,
    is_deleted=False,
    is_disabled_seatmap=False,
    is_empty_seatmap=False,
    remaining_place=78,
    internet_remaining_place=11,
    showtime=datetime(2022, 7, 1, 12, 00, 00),
    shows_tariff_pos_type_collection=[ShowTariffCDS(tariff=IdObjectCDS(id=4))],
    screen=IdObjectCDS(id=1),
    media=IdObjectCDS(id=123),
    showsMediaoptionsCollection=[ShowsMediaoptionsCDS(mediaoptionsid=IdObjectCDS(id=5))],
)

MOVIE_OTHER_SHOW_1 = ShowCDS(
    id=1,
    is_cancelled=False,
    is_deleted=False,
    is_disabled_seatmap=False,
    is_empty_seatmap=False,
    remaining_place=77,
    internet_remaining_place=10,
    showtime=datetime(2022, 6, 20, 11, 00, 00),
    shows_tariff_pos_type_collection=[ShowTariffCDS(tariff=IdObjectCDS(id=4))],
    screen=IdObjectCDS(id=1),
    media=IdObjectCDS(id=88888),
    showsMediaoptionsCollection=[ShowsMediaoptionsCDS(mediaoptionsid=IdObjectCDS(id=5))],
)

MOVIE_OTHER_SHOW_2 = ShowCDS(
    id=2,
    is_cancelled=False,
    is_deleted=False,
    is_disabled_seatmap=False,
    is_empty_seatmap=False,
    remaining_place=77,
    internet_remaining_place=10,
    showtime=datetime(2022, 7, 1, 12, 00, 00),
    shows_tariff_pos_type_collection=[ShowTariffCDS(tariff=IdObjectCDS(id=4))],
    screen=IdObjectCDS(id=1),
    media=IdObjectCDS(id=88888),
    showsMediaoptionsCollection=[ShowsMediaoptionsCDS(mediaoptionsid=IdObjectCDS(id=5))],
)

CINEMA_WITH_INTERNET_SALE_GAUGE_ACTIVE_TRUE = {
    "id": "cinema_id_test",
    "internetsalegaugeactive": True,
    "cinemaParameters": [
        {
            "id": 1,
            "key": "scheduleTemplate",
            "value": None,
        }
    ],
}

CINEMA_WITH_INTERNET_SALE_GAUGE_ACTIVE_FALSE = {
    "id": "cinema_id_test",
    "internetsalegaugeactive": False,
    "cinemaParameters": [
        {
            "id": 1,
            "key": "scheduleTemplate",
            "value": None,
        }
    ],
}

SHOW_1 = {
    "id": 1,
    "canceled": False,
    "deleted": False,
    "disableseatmap": False,
    "seatmap": False,
    "remainingplace": 77,
    "internetremainingplace": 10,
    "showtime": "2022-06-20T11:00:00.000+0200",
    "showsTariffPostypeCollection": [
        {
            "tariffid": {"id": 4},
        }
    ],
    "screenid": {"id": 1},
    "mediaid": {"id": 123},
    "showsMediaoptionsCollection": [
        {"mediaoptionsid": {"id": 1}},
        {"mediaoptionsid": {"id": 2}},
    ],
}

SHOW_2 = {
    "id": 2,
    "canceled": False,
    "deleted": False,
    "disableseatmap": False,
    "seatmap": False,
    "remainingplace": 78,
    "internetremainingplace": 10,
    "showtime": "2022-07-01T12:00:00.000+0200",
    "showsTariffPostypeCollection": [{"tariffid": {"id": 5}}],
    "screenid": {"id": 1},
    "mediaid": {"id": 51},
    "showsMediaoptionsCollection": [{"mediaoptionsid": {"id": 5}}],
}

VOUCHER_TYPE_PC_1 = {
    "id": 66,
    "code": "PSCULTURE",
    "tariffid": {"id": 4, "price": 5, "active": True, "label": "pass Culture"},
}

VOUCHER_TYPE_PC_2 = {
    "id": 67,
    "code": "PSCULTURE",
    "tariffid": {"id": 5, "price": 6.5, "active": True, "label": "pass Culture"},
}

MOVIE_3 = {
    "id": 123,
    "title": "Coupez !",
    "duration": 120,
    "storyline": "Ca tourne mal",
    "visa": "123456",
    "posterpath": "https://example.com/coupez.png",
}

MEDIA_OPTIONS = [
    {
        "ticketlabel": "3D",
        "requiresequipment": True,
        "optiontype": 1,
        "optionorder": 6,
        "nationalcode": "3D",
        "label": "PICTURE_3D",
        "id": 1,
        "deleted": False,
        "defaultoption": False,
        "cinemaid": "cdsdemorc1",
    },
    {
        "ticketlabel": "VF",
        "requiresequipment": False,
        "optiontype": 4,
        "optionorder": 3,
        "nationalcode": "1",
        "label": "VERSION_ORIGINAL_LOCAL",
        "id": 2,
        "groupid": 3,
        "deleted": False,
        "defaultoption": False,
        "cinemaid": "cdsdemorc1",
    },
    {
        "ticketlabel": "VO",
        "requiresequipment": False,
        "optiontype": 4,
        "optionorder": 2,
        "nationalcode": "2",
        "label": "VERSION_ORIGINAL",
        "id": 3,
        "groupid": 3,
        "deleted": False,
        "defaultoption": False,
        "cinemaid": "cdsdemorc1",
    },
    {
        "ticketlabel": "MUET",
        "requiresequipment": False,
        "optiontype": 4,
        "optionorder": 4,
        "nationalcode": "6",
        "label": "VERSION_MUET",
        "id": 4,
        "groupid": 3,
        "deleted": False,
        "defaultoption": False,
        "cinemaid": "cdsdemorc1",
    },
    {
        "requiresequipment": False,
        "optiontype": 1,
        "optionorder": 1,
        "nationalcode": "NUM",
        "label": "PICTURE_2K",
        "id": 5,
        "groupid": 1,
        "deleted": False,
        "defaultoption": True,
        "cinemaid": "cdsdemorc1",
    },
]
