from datetime import datetime
from typing import Optional

from models import BankInformation


def get_last_update_from_bank_information(last_provider_id: Optional[int] = None) -> datetime:
    last_bank_information_retrieved = BankInformation.query \
        .with_entities(BankInformation.dateModifiedAtLastProvider) \
        .filter_by(lastProviderId=last_provider_id) \
        .order_by(BankInformation.dateModifiedAtLastProvider.desc()) \
        .first()
    if last_bank_information_retrieved:
        return last_bank_information_retrieved.dateModifiedAtLastProvider
    else:
        first_of_january_1900 = datetime(1900, 1, 1)
        return first_of_january_1900


def get_by_application_id(application_id: int) -> Optional[BankInformation]:
    return BankInformation.query \
        .filter_by(applicationId=application_id) \
        .one_or_none()


def get_by_offerer_and_venue(offerer_id: int, venue_id: int) -> Optional[BankInformation]:
    return BankInformation.query \
        .filter_by(offererId=offerer_id) \
        .filter_by(venueId=venue_id) \
        .one_or_none()
