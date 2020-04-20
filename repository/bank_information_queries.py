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
