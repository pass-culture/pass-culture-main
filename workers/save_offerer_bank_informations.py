from local_providers import OffererBankInformationProvider
from local_providers.provider_manager import launch_provider_on_data
from workers.decorators import job_context




@job_context
def pc_synchronize_new_bank_informations(application_id: str):
    launch_provider_on_data("OffererBankInformationProvider", [application_id])

