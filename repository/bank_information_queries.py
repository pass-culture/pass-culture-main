from datetime import datetime
from typing import Optional

from models import BankInformation


def get_by_application_id(application_id: int) -> Optional[BankInformation]:
    return BankInformation.query \
        .filter_by(applicationId=application_id) \
        .first()


def get_by_offerer_and_venue(offerer_id: int, venue_id: int) -> Optional[BankInformation]:
    return BankInformation.query \
        .filter_by(offererId=offerer_id) \
        .filter_by(venueId=venue_id) \
        .one_or_none()
