import os
from workers.decorators import job_context
from rq.decorators import job
from datetime import datetime

from utils.date import DATE_ISO_FORMAT
from connectors.api_demarches_simplifiees import get_application_details, DmsApplicationStates
from models import BankInformation
from models.bank_information import BankInformationStatus
from repository import repository, offerer_queries, bank_information_queries
from workers import worker
from domain.bank_information import status_weight

PROCEDURE_ID = os.environ.get(
    'DEMARCHES_SIMPLIFIEES_RIB_OFFERER_PROCEDURE_ID')
TOKEN = os.environ.get('DEMARCHES_SIMPLIFIEES_TOKEN')


@job(worker.redis_queue, connection=worker.conn)
@job_context
def synchronize_bank_informations(application_id: str, provider_name: str):
    if provider_name == 'offerer':
        save_offerer_bank_informations(application_id)
    elif provider_name == 'venue':
        save_venue_bank_informations(application_id)


def save_offerer_bank_informations(application_id: str):
    application_details = get_application_details(application_id, procedure_id=PROCEDURE_ID, token=TOKEN)

    siren = application_details['dossier']['entreprise']['siren']
    offerer = offerer_queries.find_by_siren(siren)

    if offerer is None:
        raise NoRefererException(f'Offerer not found for application id {application_id}.')

    save_bank_information(application_details, offerer.id)


def save_bank_information(application_details, offerer_id):
    status = _get_status_from_demarches_simplifiees_application_state(
        DmsApplicationStates[application_details['dossier']['state']])
    application_id = application_details['dossier']["id"]

    bank_information = bank_information_queries.get_by_application_id(
        application_id)

    if bank_information is None:
        bank_information = bank_information_queries.get_by_offerer(
            offerer_id) or BankInformation()

        if (bank_information.dateModifiedAtLastProvider is not None and
                datetime.strptime(application_details['dossier']['updated_at'], DATE_ISO_FORMAT) < bank_information.dateModifiedAtLastProvider):
            return
        if (bank_information.status and
                status_weight[status] < status_weight[bank_information.status]):
            return

    bank_information.applicationId = int(application_id)
    bank_information.offererId = offerer_id
    bank_information.venuId = None
    bank_information.status = status

    if status == BankInformationStatus.ACCEPTED:
        bank_information.iban = _find_value_in_fields(
            application_details['dossier']["champs"], "IBAN")
        bank_information.bic = _find_value_in_fields(
            application_details['dossier']["champs"], "BIC")
    else:
        bank_information.iban = None
        bank_information.bic = None

    repository.save(bank_information)


def save_venue_bank_informations(application_id: str):
    return


def _get_status_from_demarches_simplifiees_application_state(state: str) -> BankInformationStatus:
    rejected_states = [DmsApplicationStates.refused,
                       DmsApplicationStates.without_continuation]
    accepted_states = [DmsApplicationStates.closed]
    draft_states = [DmsApplicationStates.received, DmsApplicationStates.initiated]

    if state in rejected_states:
        return BankInformationStatus.REJECTED
    elif state in accepted_states:
        return BankInformationStatus.ACCEPTED
    elif state in draft_states:
        return BankInformationStatus.DRAFT

    raise Exception(f'Unknown Demarches Simplifiées state {state}')


def _find_value_in_fields(fields, value_name):
    for field in fields:
        if field["type_de_champ"]["libelle"] == value_name:
            return field["value"]


class NoRefererException(Exception):
    pass
