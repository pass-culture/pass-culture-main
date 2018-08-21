from datetime import datetime, timedelta

import pytest
from sqlalchemy.exc import IntegrityError

from models import PcObject
from tests.conftest import clean_database
from utils.test_utils import create_event_occurrence, create_thing_offer, create_venue, create_offerer


@pytest.mark.standalone
@clean_database
def test_beginning_datetime_cannot_be_after_end_datetime(app):
    # given
    offer = create_thing_offer(create_venue(create_offerer()))
    now = datetime.utcnow()
    beginning = now - timedelta(days=5)
    end = beginning - timedelta(days=1)
    occurrence = create_event_occurrence(offer, beginning, end)

    # when
    with pytest.raises(IntegrityError):
        PcObject.check_and_save(occurrence)
