import datetime

import pytest
import pytz

from pcapi.core.payments import utils


@pytest.mark.parametrize(
    "last_day_as_str, expected_result",
    [
        # CET (UTC+1)
        (datetime.date(2020, 12, 31), datetime.datetime(2020, 12, 31, 23, 0, tzinfo=pytz.utc)),
        (datetime.date(2021, 2, 28), datetime.datetime(2021, 2, 28, 23, 0, tzinfo=pytz.utc)),
        # CEST (UTC+2)
        (datetime.date(2021, 3, 31), datetime.datetime(2021, 3, 31, 22, 0, tzinfo=pytz.utc)),
    ],
)
def test_get_cutoff_as_datetime(last_day_as_str, expected_result):
    assert utils.get_cutoff_as_datetime(last_day_as_str) == expected_result
