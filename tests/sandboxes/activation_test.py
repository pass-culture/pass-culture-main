from models import Stock

from sandboxes.scripts.save_sandbox import save_sandbox
from tests.conftest import clean_database
from tests.model_creators.provider_creators import saveCounts, assertCreatedCounts
from utils.logger import logger


@clean_database
def test_save_activation_sandbox(app):
    # given
    saveCounts()
    logger_info = logger.info
    logger.info = lambda o: None

    # when
    save_sandbox('activation')

    # then
    assertCreatedCounts(
        Booking=0,
        Deposit=0,
        Mediation=2,
        Offer=1,
        Offerer=1,
        Product=1,
        Recommendation=0,
        Stock=1,
        User=0,
        UserOfferer=0,
    )

    assert Stock.query.first().available == 10000

    # teardown
    logger.info = logger_info
