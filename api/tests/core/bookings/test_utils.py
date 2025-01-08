import datetime
import importlib

import pytest
import pytz
import time_machine

from pcapi.core.bookings import utils
from pcapi.core.categories import subcategories_v2 as subcategories


@pytest.mark.parametrize(
    "subcategory_id, cooldown_datetime",
    [
        (subcategories.SEANCE_CINE.id, datetime.datetime(2025, 1, 31, 12, 34, 26)),
        (subcategories.LIVRE_PAPIER.id, datetime.datetime(2025, 1, 1, 12, 34, 26)),
        (subcategories.SUPPORT_PHYSIQUE_MUSIQUE_CD.id, datetime.datetime(2025, 1, 1, 12, 34, 26)),
        (subcategories.SUPPORT_PHYSIQUE_MUSIQUE_VINYLE.id, datetime.datetime(2025, 1, 1, 12, 34, 26)),
        ("ANY_OTHER_SUB_CATEGORY_ID", datetime.datetime(2025, 2, 1, 12, 34, 26)),
    ],
)
@time_machine.travel(datetime.datetime(2025, 2, 1, 12, 34, 26))
def test_get_cooldown_datetime_by_subcategories(subcategory_id, cooldown_datetime):
    assert utils.get_cooldown_datetime_by_subcategories(subcategory_id) == cooldown_datetime


@pytest.mark.settings(SUGGEST_REACTION_SHORT_COOLDOWN_IN_SECONDS=30, SUGGEST_REACTION_LONG_COOLDOWN_IN_SECONDS=300)
def test_get_cooldown_datetime_by_subcategories_env():
    # Reload utils to recalculate SUGGEST_REACTION_COOLDOWN_IN_SECONDS impacted by env vars
    importlib.reload(utils)

    with time_machine.travel(datetime.datetime(2025, 2, 1, 12, 34, 26)):
        subcategory_id = subcategories.SEANCE_CINE.id
        cooldown_datetime = datetime.datetime(2025, 2, 1, 12, 33, 56)
        assert utils.get_cooldown_datetime_by_subcategories(subcategory_id) == cooldown_datetime

    with time_machine.travel(datetime.datetime(2025, 2, 1, 12, 34, 26)):
        subcategory_id = subcategories.SUPPORT_PHYSIQUE_MUSIQUE_CD.id
        cooldown_datetime = datetime.datetime(2025, 2, 1, 12, 29, 26)
        assert utils.get_cooldown_datetime_by_subcategories(subcategory_id) == cooldown_datetime


@pytest.mark.parametrize(
    "date_period, timezone, expected_result",
    [
        (
            [datetime.date(2024, 12, 11), datetime.date(2024, 12, 12)],
            "Europe/Paris",
            (
                datetime.datetime(2024, 12, 10, 23, 0, 0, tzinfo=pytz.utc),
                datetime.datetime(2024, 12, 12, 22, 59, 59, tzinfo=pytz.utc),
            ),
        ),
        (  # dates not ordered
            [datetime.date(2024, 12, 25), datetime.date(2024, 12, 4)],
            "Europe/Paris",
            (
                datetime.datetime(2024, 12, 3, 23, 0, 0, tzinfo=pytz.utc),
                datetime.datetime(2024, 12, 25, 22, 59, 59, tzinfo=pytz.utc),
            ),
        ),
    ],
)
def test_convert_date_period_to_utc_datetime_period(date_period, timezone, expected_result):
    result = utils.convert_date_period_to_utc_datetime_period(date_period, timezone)
    assert result == expected_result
