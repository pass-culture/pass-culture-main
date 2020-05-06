from local_providers import OffererBankInformationProvider
from local_providers.provider_manager import do_update

from workers.decorators import job_context




@job_context
def pc_synchronize_new_bank_informations(application_id: str):
    provider_class = OffererBankInformationProvider
    try:
        provider = provider_class([application_id])
        do_update(provider, limit=None)
    except Exception as error:
        print(error)

