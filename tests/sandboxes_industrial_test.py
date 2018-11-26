import pytest
from tests.conftest import clean_database

from sandboxes.scripts.save_sandbox import save_sandbox
from utils.logger import logger
from utils.test_utils import assertCreatedCounts, \
                             saveCounts

@clean_database
@pytest.mark.standalone
def test_save_industrial_sandbox(app):
    savedCounts = {}
    saveCounts(app)
    with app.app_context():
        logger_info = logger.info
        logger.info = lambda o: None
        save_sandbox('industrial')
        logger.info = logger_info
        assertCreatedCounts(
            app,
            Deposit=4,
            Event=7,
            EventOccurrence=108,
            Mediation=72,
            Offer=108,
            Offerer=6,
            Stock=144,
            Thing=11,
            User=12,
            UserOfferer=36,
            Venue=12
        )
