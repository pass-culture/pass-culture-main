import pytest

from sandboxes.scripts.testcafe_helpers import get_all_testcafe_helpers
from sandboxes.scripts.save_sandbox import save_sandbox
from tests.conftest import clean_database
from tests.test_utils import assertCreatedCounts, \
                             saveCounts
from utils.logger import logger


@clean_database
@pytest.mark.standalone
def test_save_industrial_sandbox(app):
    # given
    saveCounts(app)
    with app.app_context():
        logger_info = logger.info
        logger.info = lambda o: None

        #when
        save_sandbox('industrial')
        logger.info = logger_info

        # then
        assertCreatedCounts(
            app,
            Booking=43,
            Deposit=6,
            Event=56,
            EventOccurrence=78,
            Mediation=55,
            Offer=105,
            Offerer=13,
            Recommendation=111,
            Stock=101,
            Thing=77,
            User=49,
            UserOfferer=37,
            Venue=21
        )

@clean_database
@pytest.mark.standalone
def test_get_all_testcafe_helpers_find_all_items(app):
    # given
    with app.app_context():
        # given
        logger_info = logger.info
        logger.info = lambda o: None
        save_sandbox('industrial')
        logger.info = logger_info

        # when
        testcafe_helpers = get_all_testcafe_helpers()
        values = testcafe_helpers.values()

        # then
        assert None not in values
