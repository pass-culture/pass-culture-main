import pytest
from tests.conftest import clean_database

from sandboxes.scripts.save_sandbox import save_sandbox
from utils.logger import logger
from tests.test_utils import assertCreatedCounts, \
                             saveCounts

@clean_database
@pytest.mark.standalone
def test_save_handmade_sandbox(app):
    # given
    saveCounts()
    logger_info = logger.info
    logger.info = lambda o: None

    # when
    save_sandbox('handmade')

    # then
    assertCreatedCounts(
        Booking=2,
        Deposit=1,
        Event=4,
        EventOccurrence=5,
        Mediation=5,
        Offer=7,
        Offerer=7,
        Recommendation=6,
        Stock=9,
        Thing=3,
        User=10,
        UserOfferer=7,
        Venue=8
    )

    # teardown
    logger.info = logger_info
