import logging

import pytest

from pcapi.model_creators.provider_creators import assert_created_counts
from pcapi.model_creators.provider_creators import save_counts
from pcapi.models import Stock
from pcapi.sandboxes.scripts.save_sandbox import save_sandbox


logger = logging.getLogger(__name__)


@pytest.mark.usefixtures("db_session")
def test_save_activation_sandbox(app):
    # given
    save_counts()
    logger_info = logger.info
    logger.info = lambda o: None

    # when
    save_sandbox("activation")

    # then
    assert_created_counts(
        Booking=0,
        Deposit=0,
        Mediation=0,
        Offer=1,
        Offerer=1,
        Product=1,
        Stock=1,
        User=0,
        UserOfferer=0,
    )

    assert Stock.query.first().quantity == 10000

    # teardown
    logger.info = logger_info
