import os
from workers.decorators import job_context
from rq.decorators import job

from connectors.api_demarches_simplifiees import get_application_details, DmsApplicationStates
from models import BankInformation
from models.bank_information import BankInformationStatus
from repository import repository, offerer_queries
from workers import worker

PROCEDURE_ID = os.environ.get(
    'DEMARCHES_SIMPLIFIEES_RIB_OFFERER_PROCEDURE_ID')
TOKEN = os.environ.get('DEMARCHES_SIMPLIFIEES_TOKEN')

REJECTED_STATES = [DmsApplicationStates.refused,
                   DmsApplicationStates.without_continuation]
ACCEPTED_STATES = [DmsApplicationStates.closed]
DRAFT_STATES = [DmsApplicationStates.received, DmsApplicationStates.initiated]

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

    bank_information = offerer.bankInformation or BankInformation()

    bank_information.applicationId = int(application_id)
    state = DmsApplicationStates[application_details['dossier']['state']]

    if state in REJECTED_STATES:
        bank_information.status = BankInformationStatus.REJECTED
        bank_information.iban = None
        bank_information.bic = None

    elif state in ACCEPTED_STATES:
        bank_information.status = BankInformationStatus.ACCEPTED
        bank_information.iban = _find_value_in_fields(
            application_details['dossier']["champs"], "IBAN")
        bank_information.bic = _find_value_in_fields(
            application_details['dossier']["champs"], "BIC")

    elif state in DRAFT_STATES:
        bank_information.status = BankInformationStatus.DRAFT
        bank_information.iban = None
        bank_information.bic = None

    repository.save(bank_information)


def save_venue_bank_informations(application_id: str):
    return



def _find_value_in_fields(fields, value_name):
    for field in fields:
        if field["type_de_champ"]["libelle"] == value_name:
            return field["value"]


class NoRefererException(Exception):
    pass