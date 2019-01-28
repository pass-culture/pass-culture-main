import pytest

from sandboxes.scripts.save_sandbox import save_sandbox
from tests.conftest import clean_database
from utils.logger import logger
from utils.test_utils import assertCreatedCounts, \
    saveCounts


@clean_database
@pytest.mark.standalone
def test_save_industrial_sandbox(app):
    saveCounts(app)
    with app.app_context():
        logger_info = logger.info
        logger.info = lambda o: None
        save_sandbox('industrial')
        logger.info = logger_info
        assertCreatedCounts(
            app,
            Booking=20,
            Deposit=6,
            Event=32,
            EventOccurrence=48,
            Mediation=38,
            Offer=71,
            Offerer=13,
            Recommendation=63,
            Stock=44,
            Thing=33,
            User=21,
            UserOfferer=121,
            Venue=21
        )
