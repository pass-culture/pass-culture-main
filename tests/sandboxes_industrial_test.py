from pprint import pprint

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
        Booking=58,
        Deposit=6,
        Mediation=86,
        Offer=105,
        Offerer=13,
        Payment=12,
        Product=147,
        Recommendation=117,
        Stock=101,
        User=51,
        UserOfferer=125,
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
    pprint(values)
    assert None not in values

    # teardown
    logger.info = logger_info
