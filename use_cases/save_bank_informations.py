import os
from workers.decorators import job_context
from datetime import datetime

from utils.date import DATE_ISO_FORMAT
from connectors.api_demarches_simplifiees import get_application_details, DmsApplicationStates
from models import BankInformation
from models.bank_information import BankInformationStatus
from repository import bank_information_queries, offerer_queries, repository, venue_queries
from workers import worker
from domain.bank_information import check_offerer_presence, check_venue_presence, check_venue_queried_by_name, status_weight

OFFERER_PROCEDURE_ID = os.environ.get(
    'DEMARCHES_SIMPLIFIEES_RIB_OFFERER_PROCEDURE_ID')
VENUE_PROCEDURE_ID = os.environ.get(
    'DEMARCHES_SIMPLIFIEES_RIB_VENUE_PROCEDURE_ID')
TOKEN = os.environ.get('DEMARCHES_SIMPLIFIEES_TOKEN')
FIELD_FOR_VENUE_WITH_SIRET = "Si vous souhaitez renseigner les coordonn\u00e9es bancaires d'un lieu avec SIRET, merci de saisir son SIRET :"
FIELD_FOR_VENUE_WITHOUT_SIRET = "Si vous souhaitez renseigner les coordonn\u00e9es bancaires d'un lieu sans SIRET, merci de saisir le \"Nom du lieu\", \u00e0 l'identique de celui dans le pass Culture Pro :"



def save_offerer_bank_informations(application_id: str):
    application_details = get_application_details(application_id, procedure_id=OFFERER_PROCEDURE_ID, token=TOKEN)

    siren = application_details['dossier']['entreprise']['siren']
    offerer = offerer_queries.find_by_siren(siren)

    check_offerer_presence(offerer)

    save_bank_information(application_details, offerer.id, None)


def save_venue_bank_informations(application_id: str):
    application_details = get_application_details(application_id, procedure_id=VENUE_PROCEDURE_ID, token=TOKEN)

    siren = application_details['dossier']['entreprise']['siren']
    offerer = offerer_queries.find_by_siren(siren)

    check_offerer_presence(offerer)

    siret = _find_value_in_fields(
        application_details['dossier']["champs"], FIELD_FOR_VENUE_WITH_SIRET)
    if siret:
        venue = venue_queries.find_by_managing_offerer_id_and_siret(
            offerer.id, siret)
        check_venue_presence(venue)
    else:
        name = _find_value_in_fields(
            application_details['dossier']["champs"], FIELD_FOR_VENUE_WITHOUT_SIRET)
        venues = venue_queries.find_venue_without_siret_by_managing_offerer_id_and_name(
            offerer.id, name)
        check_venue_queried_by_name(venues)
        venue = venues[0]

    save_bank_information(application_details, None,  venue.id)


def save_bank_information(application_details, offerer_id, venue_id):
    status = _get_status_from_demarches_simplifiees_application_state(
        DmsApplicationStates[application_details['dossier']['state']])
    application_id = application_details['dossier']["id"]

    bank_information = bank_information_queries.get_by_application_id(
        application_id)

    if bank_information is None:
        bank_information = bank_information_queries.get_by_offerer_and_venue(
            offerer_id, venue_id) or BankInformation()

        if (bank_information.dateModifiedAtLastProvider is not None and
                datetime.strptime(application_details['dossier']['updated_at'], DATE_ISO_FORMAT) < bank_information.dateModifiedAtLastProvider):
            return
        if (bank_information.status and
                status_weight[status] < status_weight[bank_information.status]):
            return

    bank_information.applicationId = int(application_id)
    bank_information.offererId = offerer_id
    bank_information.venueId = venue_id
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

