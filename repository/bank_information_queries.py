from datetime import datetime

from models import BankInformation


def get_last_update_from_bank_information(last_provider_id=None):
    last_bank_information_retrieved = BankInformation.query.filter_by(lastProviderId=last_provider_id).order_by(
        BankInformation.dateModifiedAtLastProvider.desc()).first()
    if last_bank_information_retrieved:
        return last_bank_information_retrieved.dateModifiedAtLastProvider
    else:
        first_of_january_1900 = datetime(1900, 1, 1)
        return first_of_january_1900
