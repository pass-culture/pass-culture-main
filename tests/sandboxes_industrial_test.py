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
            Booking=42,
            Deposit=6,
            Event=56,
            EventOccurrence=78,
            Mediation=55,
            Offer=105,
            Offerer=13,
            Recommendation=105,
            Stock=101,
            Thing=77,
            User=21,
            UserOfferer=121,
            Venue=21
        )
