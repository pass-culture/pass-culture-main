from datetime import datetime
from typing import Callable

from connectors.api_demarches_simplifiees import get_all_applications_for_procedure
from utils.date import DATE_ISO_FORMAT


def get_all_application_ids_from_demarches_simplifiees_procedure(procedure_id: str, token: str, last_update: datetime,
                                                                 get_all_applications_for_procedure_in_demarches_simplifiees:
                                                                 Callable[[str,
                                                                           str], dict] = get_all_applications_for_procedure):
    applications = get_all_applications_for_procedure_in_demarches_simplifiees(procedure_id, token)
    applications_to_process = [application['id'] for application in applications['dossiers'] if
                               _needs_processing(application, last_update)]
    return applications_to_process


def _needs_processing(application: dict, last_update: datetime) -> dict:
    return application['state'] == 'closed' and (
                datetime.strptime(application['updated_at'], DATE_ISO_FORMAT) > last_update)
