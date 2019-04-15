import pytest

from sandboxes.scripts.save_sandbox import save_sandbox
from sandboxes.scripts.testcafe_helpers import get_all_testcafe_helpers
from tests.conftest import clean_database
from tests.test_utils import assertCreatedCounts, \
    saveCounts
from utils.logger import logger


@clean_database
@pytest.mark.standalone
def test_save_industrial_sandbox(app):
    # given
    saveCounts()
    logger_info = logger.info
    logger.info = lambda o: None

    # when
    save_sandbox('industrial')

    # then
    assertCreatedCounts(
        Offerer=13,
        Venue=21,
        Product=126,
        Offer=105,
        Stock=101,
        Mediation=55,
        User=49,
        Deposit=6,
        UserOfferer=125,
        Recommendation=102,
        Booking=40,
    )

    # teardown
    logger.info = logger_info


@clean_database
@pytest.mark.standalone
def test_get_all_testcafe_helpers_find_all_items(app):
    # given
    logger_info = logger.info
    logger.info = lambda o: None
    save_sandbox('industrial')

    # when
    testcafe_helpers = get_all_testcafe_helpers()

    # then
    values = testcafe_helpers.values()
    assert None not in values

    # teardown
    logger.info = logger_info
