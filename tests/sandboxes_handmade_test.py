import pytest
from tests.conftest import clean_database

from sandboxes.scripts.save_sandbox import save_sandbox
from utils.logger import logger
from utils.test_utils import assertCreatedCounts, \
                             saveCounts

@clean_database
@pytest.mark.standalone
def test_save_handmade_sandbox(app):
    savedCounts = {}
    saveCounts(app)
    with app.app_context():
        logger_info = logger.info
        logger.info = lambda o: None
        save_sandbox('handmade')
        logger.info = logger_info
        assertCreatedCounts(
            app,
            Booking=2,
            Deposit=1,
            Event=4,
            EventOccurrence=5,
            Mediation=3,
            Offer=6,
            Offerer=6,
            Recommendation=2,
            Stock=8,
            Thing=2,
            User=8,
            UserOfferer=6,
            Venue=7
        )
