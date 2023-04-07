from datetime import datetime

from pcapi.connectors.serialization.cine_digital_service_serializers import IdObjectCDS
from pcapi.connectors.serialization.cine_digital_service_serializers import ShowCDS
from pcapi.connectors.serialization.cine_digital_service_serializers import ShowTariffCDS
from pcapi.core.external_bookings.models import Movie


MOVIE_1 = Movie(
    id="123",
    title="Coupez !",
    duration=120,
    description="Ca tourne mal",
    visa="123456",
    posterpath="https://example.com/coupez.png",
)

MOVIE_2 = Movie(
    id="51",
    title="Top Gun",
    duration=150,
    description="Film sur les avions",
    visa="333333",
    posterpath="https://example.com/topgun.png",
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
