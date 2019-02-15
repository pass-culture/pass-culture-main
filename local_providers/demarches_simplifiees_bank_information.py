import os

from datetime import datetime

from connectors.api_demarches_simplifiees import get_application_details
from domain.retrieve_bank_account_information_for_offerers import \
    get_all_application_ids_from_demarches_simplifiees_procedure
from models import BankInformation
from models.local_provider import LocalProvider, ProvidableInfo
from models.local_provider_event import LocalProviderEventType
from repository import offerer_queries, venue_queries
from utils.date import DATE_ISO_FORMAT




class UnknownRIBAffiliation(Exception):
    pass


class BankInformationProvider(LocalProvider):
    help = ""
    identifierDescription = "siren / siret"
    identifierRegexp = None
    name = "Demarches simplifiees / Bank Information"
    objectType = BankInformation
    canCreate = True

    def __init__(self):
        super().__init__()
        self.PROCEDURE_ID = os.environ['DEMARCHES_SIMPLIFIEES_PROCEDURE_ID']
        self.TOKEN = os.environ['DEMARCHES_SIMPLIFIEES_TOKEN']

        last_bank_information_retrieved = BankInformation.query.order_by(BankInformation.dateModifiedAtLastProvider.desc()).first()
        if last_bank_information_retrieved:
            last_update = last_bank_information_retrieved.dateModifiedAtLastProvider
        else:
            last_update = datetime.strptime("1900-01-01T00:00:00.000Z", DATE_ISO_FORMAT)
        self.application_ids = iter(get_all_application_ids_from_demarches_simplifiees_procedure(self.PROCEDURE_ID, self.TOKEN, last_update))

    def __next__(self):
        self.application_id = self.application_ids.__next__()

        self.application_details = get_application_details(self.application_id, self.PROCEDURE_ID, self.TOKEN)

        if not self.application_details:
            return None

        self.bank_information_dict = retrieve_bank_information_dict_from(self.application_details)

        if self.bank_information_dict['rib_affiliation'] == "Unknown":
            self.logEvent(LocalProviderEventType.SyncError,
                          f'unknown RIB affiliation for application id {self.application_id}')
            return None

        if 'idAtProviders' not in self.bank_information_dict:
            self.logEvent(LocalProviderEventType.SyncError,
                          f'unknown siret or siren for application id {self.application_id}')
            return None

        return self.retreive_providable_info()

    def updateObject(self, bank_information):
        bank_information.iban = self.bank_information_dict['iban']
        bank_information.bic = self.bank_information_dict['bic']
        bank_information.application_id = self.bank_information_dict['application_id']
        bank_information.offererId = self.bank_information_dict[
            'offererId'] if 'offererId' in self.bank_information_dict else None
        bank_information.venueId = self.bank_information_dict[
            'venueId'] if 'venueId' in self.bank_information_dict else None

    def retreive_providable_info(self):
        providable_info = ProvidableInfo()
        providable_info.idAtProviders = self.bank_information_dict['idAtProviders']
        providable_info.type = BankInformation
        providable_info.dateModifiedAtProvider = datetime.strptime(self.application_details['dossier']['updated_at'],
                                                                   DATE_ISO_FORMAT)
        return providable_info


def _find_value_in_fields(fields, value_name):
    for field in fields:
        if field["type_de_champ"]["libelle"] == value_name:
            return field["value"]


def retrieve_bank_information_dict_from(application_details: dict) -> dict:
    bank_information_dict = dict()
    bank_information_dict['iban'] = _find_value_in_fields(application_details['dossier']["champs"], "IBAN")
    bank_information_dict['bic'] = _find_value_in_fields(application_details['dossier']["champs"], "BIC")
    bank_information_dict['application_id'] = application_details['dossier']["id"]
    bank_information_dict['rib_affiliation'] = _find_value_in_fields(application_details['dossier']["champs"],
                                                                     "Je souhaite renseigner")
    if bank_information_dict['rib_affiliation'] == "Le RIB par défaut pour toute structure liée à mon SIREN":
        siren = application_details['dossier']['entreprise']['siren']
        offerer = offerer_queries.find_by_siren(siren)
        if offerer:
            bank_information_dict['offererId'] = offerer.id
            bank_information_dict['idAtProviders'] = siren
    elif bank_information_dict['rib_affiliation'] == "Le RIB lié à un unique SIRET":
        siret = application_details['dossier']['etablissement']['siret']
        venue = venue_queries.find_by_siret(siret)
        if venue:
            bank_information_dict['venueId'] = venue.id
            bank_information_dict['idAtProviders'] = siret
    else:
        bank_information_dict['rib_affiliation'] = "Unknown"
    return bank_information_dict
