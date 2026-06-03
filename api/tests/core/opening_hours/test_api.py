import pytest

from pcapi.core.offerers import factories as offerers_factories
from pcapi.utils.date import numranges_to_timespan_str
from pcapi.utils.date import timespan_str_to_numrange


pytestmark = pytest.mark.usefixtures("db_session")


@pytest.fixture(name="venue")
def venue_fixture():
    return offerers_factories.VenueFactory()


def validate_timespans(fetched_timespans, expected_timespans):
    """Check that timespans fetched from the DB matched the input timespans

    fetched_timespans example: [NumericRange(600, 720), NumericRange(780, 1200)]
    expected_timespans example: [["10:00", "12:00"], ["13:00", "20:00"]]
    """
    expected_timespans = sorted(expected_timespans, key=lambda oh: oh[0])
    fetched_timespans = sorted(fetched_timespans, key=lambda ts: ts.lower)
    # remove unused argument and canonize string representation
    fetched_timespans = timespan_str_to_numrange(numranges_to_timespan_str(fetched_timespans))
    assert fetched_timespans == timespan_str_to_numrange(expected_timespans)
