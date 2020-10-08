from models import StockSQLEntity

from sandboxes.scripts.save_sandbox import save_sandbox
import pytest
from model_creators.provider_creators import save_counts, assert_created_counts
from utils.logger import logger


@pytest.mark.usefixtures("db_session")
def test_save_activation_sandbox(app):
    # given
    save_counts()
    logger_info = logger.info
    logger.info = lambda o: None

    # when
    save_sandbox('activation')

    # then
    assert_created_counts(
        BookingSQLEntity=0,
        Deposit=0,
        MediationSQLEntity=0,
        OfferSQLEntity=1,
        Offerer=1,
        Product=1,
        Recommendation=0,
        StockSQLEntity=1,
        UserSQLEntity=0,
        UserOfferer=0,
    )

    assert StockSQLEntity.query.first().quantity == 10000

    # teardown
    logger.info = logger_info
