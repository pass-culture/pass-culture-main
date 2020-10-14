import requests
from enum import Enum, \
    auto

from pcapi.utils.logger import json_logger

API_DEMARCHES_SIMPLIFIES = "ApiDemarchesSimplifiees"


class ApiDemarchesSimplifieesException(Exception):
    pass


class DmsApplicationStates(Enum):
    closed = auto()
    initiated = auto()
    refused = auto()
    received = auto()
    without_continuation = auto()


def get_all_applications_for_procedure(procedure_id: int,
                                       token: str,
                                       page: int = 1,
                                       results_per_page: int = 100) -> dict:
    response = requests.get(
        f"https://www.demarches-simplifiees.fr/api/v1/procedures/{procedure_id}/dossiers?token={token}&page={page}&resultats_par_page={results_per_page}")

    json_logger.info("Loading applications from Demarches Simplifiees",
                     extra={"procedure_id": procedure_id, "service": API_DEMARCHES_SIMPLIFIES, "page": page})

    if response.status_code != 200:
        json_logger.error("Loading applications from Demarches Simplifiees failed",
                          extra={"procedure_id": procedure_id, "service": API_DEMARCHES_SIMPLIFIES, "page": page})
        raise ApiDemarchesSimplifieesException(
            f'Error getting API démarches simplifiées DATA for procedure_id: {procedure_id} and token {token}')

    return response.json()


def get_application_details(application_id: int, procedure_id: int, token: str) -> dict:
    response = requests.get(
        f"https://www.demarches-simplifiees.fr/api/v1/procedures/{procedure_id}/dossiers/{application_id}?token={token}")

    json_logger.info("Loading application details from Demarches Simplifiees",
                     extra={"application_id": application_id, "procedure_id": procedure_id,
                            "service": API_DEMARCHES_SIMPLIFIES})

    if response.status_code != 200:
        json_logger.error("Loading application details failed",
                          extra={"procedure_id": procedure_id, "service": API_DEMARCHES_SIMPLIFIES,
                                 "application_id": application_id})
        raise ApiDemarchesSimplifieesException(
            f'Error getting API démarches simplifiées DATA for procedure_id: {procedure_id}, application_id: {application_id} and token {token}')

    return response.json()
