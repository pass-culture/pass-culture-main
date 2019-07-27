from sandboxes.scripts.save_sandbox import save_sandbox
from sandboxes.scripts.testcafe_helpers import get_all_getters
from tests.conftest import clean_database
from tests.test_utils import assertCreatedCounts, \
    saveCounts
from utils.logger import logger


@clean_database
def test_save_industrial_sandbox(app):
    # given
    saveCounts()
    logger_info = logger.info
    logger.info = lambda o: None

    # when
    save_sandbox('industrial')

    # then
    assertCreatedCounts(
        Booking=49,
        Deposit=8,
        Mediation=86,
        Offer=105,
        Offerer=13,
        Product=154,
        Recommendation=105,
        Stock=101,
        User=53,
        UserOfferer=125,
    )

    # teardown
    logger.info = logger_info


@clean_database
def test_all_helpers_are_returning_actual_sandbox_data(app):
    # given
    save_sandbox('industrial')

    # when
    helpers = get_all_getters()

    # then
    for k, v in helpers.items():
        assert v is not None, f"Getter '{k}' is not returning anything"
