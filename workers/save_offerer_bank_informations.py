from local_providers import OffererBankInformationProvider
from local_providers.provider_manager import do_update
from workers.worker import app
from functools import wraps

def job_context(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        worker_application = app
        with worker_application.app_context():
            return func(*args, **kwargs)

    return wrapper


@job_context
def pc_synchronize_new_bank_informations(application_id: str):
    provider_class = OffererBankInformationProvider
    try:
        provider = provider_class([application_id])
        do_update(provider, limit=None)
    except Exception as error:
        print(error)

