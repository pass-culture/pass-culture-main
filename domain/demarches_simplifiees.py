from datetime import datetime
from typing import Callable, List

from connectors.api_demarches_simplifiees import get_all_applications_for_procedure
from utils.date import DATE_ISO_FORMAT
from utils.logger import logger


def get_all_application_ids_for_procedure(
        procedure_id: str, token: str, last_update: datetime,
        get_all_applications: Callable = get_all_applications_for_procedure
) -> List[int]:
    current_page = 1
    number_of_pages = 1
    application_ids = []

    while current_page <= number_of_pages:
        api_response = get_all_applications(procedure_id, token, page=current_page, results_per_page=100)
        number_of_pages = api_response['pagination']['nombre_de_page']
        logger.info('[IMPORT DEMARCHES SIMPLIFIEES] page %s of %s' % (current_page, number_of_pages))

        needs_processing = [application for application in api_response['dossiers'] if
                            _needs_processing(application, last_update)]
        logger.info('[IMPORT DEMARCHES SIMPLIFIEES] %s applications to process' % len(needs_processing))
        application_ids += needs_processing

        current_page += 1

    logger.info('[IMPORT DEMARCHES SIMPLIFIEES] Total : %s applications' % len(application_ids))
    sorted_applications = sorted(application_ids,
                                 key=lambda k: datetime.strptime(k['updated_at'], DATE_ISO_FORMAT))
    application_ids_to_process = [application['id'] for application in sorted_applications]
    return application_ids_to_process


def _needs_processing(application: dict, last_update: datetime) -> bool:
    return _is_closed(application) and _was_last_updated_after(application, last_update)


def _is_closed(application: dict) -> bool:
    return application['state'] == 'closed'


def _was_last_updated_after(application: dict, last_update: datetime) -> bool:
    return datetime.strptime(application['updated_at'], DATE_ISO_FORMAT) >= last_update
