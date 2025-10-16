MANY_SHOWS_RESPONSE_JSON = [
    {
        "id": 1,
        "remaining_place": 98,
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
        "mediaid": {"id": 1},
        "showsMediaoptionsCollection": [
            {"mediaoptionsid": {"id": 12}},
        ],
    },
    {
        "id": 2,
        "remaining_place": 120,
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
        "mediaid": {"id": 1},
        "showsMediaoptionsCollection": [
            {"mediaoptionsid": {"id": 12}},
            {"mediaoptionsid": {"id": 14}},
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
        "mediaid": {"id": 2},
        "showsMediaoptionsCollection": [
            {"mediaoptionsid": {"id": 13}},
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

MEDIA_RESPONSE_JSON = [
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
        "id": 3,
        "title": "Test movie #3",
        "duration": 6600,
        "storyline": "Test description #3",
        # No visanumber
    },
]

MEDIA_OPTIONS_RESPONSE_JSON = [
    {"id": 12, "label": "label #1", "ticketlabel": "VF"},
    {"id": 13, "label": "label #23", "ticketlabel": "VO"},
    {"id": 14, "label": "label #23", "ticketlabel": "3D"},
    {"id": 53, "label": "label #53"},
]

VOUCHER_TYPES_RESPONSE_JSON = [
    {"id": 1, "code": "TESTCODE", "tariffid": {"id": 2, "price": 5, "active": True, "labeltariff": ""}},
    {
        "id": 2,
        "code": "PSCULTURE",
        "tariffid": {"id": 96, "price": 5, "active": True, "labeltariff": "Tarif pass Culture"},
    },
    {"id": 3, "code": "PSCULTURE", "tariffid": {"id": 97, "price": 6, "active": True, "labeltariff": "Tarif PC"}},
    {"id": 4, "code": "PSCULTURE"},
    {"id": 5, "code": None},
]

CINEMAS_RESPONSE_JSON = [
    {"id": "venue_id_at_provider", "is_internet_sale_gauge_active": False, "cinema_parameters": []}
]
