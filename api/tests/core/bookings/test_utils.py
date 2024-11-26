import datetime
import importlib

import pytest
import time_machine

import pcapi.core.bookings.utils as utils
from pcapi.core.categories import subcategories_v2 as subcategories
from pcapi.core.testing import override_settings


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


@override_settings(SUGGEST_REACTION_SHORT_COOLDOWN_IN_SECONDS=30, SUGGEST_REACTION_LONG_COOLDOWN_IN_SECONDS=300)
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
