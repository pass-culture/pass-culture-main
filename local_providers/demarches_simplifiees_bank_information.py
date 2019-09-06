import os
from datetime import datetime
from typing import Dict

from connectors.api_demarches_simplifiees import get_application_details
from domain.bank_account import format_raw_iban_or_bic
from domain.demarches_simplifiees import get_all_application_ids_for_procedure
from local_providers.local_provider import LocalProvider
from local_providers.providable_info import ProvidableInfo
from models import BankInformation
from models.local_provider_event import LocalProviderEventType
from repository import offerer_queries, venue_queries
from repository.bank_information_queries import get_last_update_from_bank_information
from scripts.payment.bank_information_retrial import retry_linked_payments
from utils.date import DATE_ISO_FORMAT


class UnknownRibAffiliation(Exception):
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
        self.PROCEDURE_ID = os.environ.get('DEMARCHES_SIMPLIFIEES_RIB_PROCEDURE_ID', None)
        self.TOKEN = os.environ.get('DEMARCHES_SIMPLIFIEES_TOKEN', None)

        most_recent_known_application_date = get_last_update_from_bank_information()

        self.application_ids = iter(
            get_all_application_ids_for_procedure(self.PROCEDURE_ID, self.TOKEN,
                                                  most_recent_known_application_date))

    def __next__(self):
        self.application_id = next(self.application_ids)

        self.application_details = get_application_details(self.application_id, self.PROCEDURE_ID, self.TOKEN)

        self.bank_information_dict = self.retrieve_bank_information(self.application_details)

        if 'idAtProviders' not in self.bank_information_dict:
            self.logEvent(LocalProviderEventType.SyncError,
                          f'unknown siret or siren for application id {self.application_id}')
            return None

        return self.retrieve_providable_info()

    def updateObject(self, bank_information):
        bank_information.iban = format_raw_iban_or_bic(self.bank_information_dict['iban'])
        bank_information.bic = format_raw_iban_or_bic(self.bank_information_dict['bic'])
        bank_information.applicationId = self.bank_information_dict['applicationId']
        bank_information.offererId = self.bank_information_dict.get('offererId', None)
        bank_information.venueId = self.bank_information_dict.get('venueId', None)

    def save_chunks(self, chunk_to_insert: Dict[str, BankInformation], chunk_to_update: Dict[str, BankInformation],
                    providable_info: ProvidableInfo):
        super(BankInformationProvider, self).save_chunks(chunk_to_insert, chunk_to_update, providable_info)
        bank_information_list = list(chunk_to_insert.values()) + list(chunk_to_update.values())
        retry_linked_payments(bank_information_list)

    def retrieve_providable_info(self):
        providable_info = ProvidableInfo()
        providable_info.id_at_providers = self.bank_information_dict['idAtProviders']
        providable_info.type = BankInformation
        providable_info.date_modified_at_provider = datetime.strptime(self.application_details['dossier']['updated_at'],
                                                                      DATE_ISO_FORMAT)
        return providable_info

    def retrieve_bank_information(self, application_details: dict) -> dict:
        bank_information_dict = dict()
        bank_information_dict['iban'] = _find_value_in_fields(application_details['dossier']["champs"], "IBAN")
        bank_information_dict['bic'] = _find_value_in_fields(application_details['dossier']["champs"], "BIC")
        bank_information_dict['applicationId'] = application_details['dossier']["id"]
        bank_information_dict['ribAffiliation'] = _find_value_in_fields(application_details['dossier']["champs"],
                                                                        "Je souhaite renseigner")
        if bank_information_dict['ribAffiliation'] == "Le RIB par défaut pour toute structure liée à mon SIREN":
            siren = application_details['dossier']['entreprise']['siren']
            offerer = offerer_queries.find_by_siren(siren)
            if offerer:
                bank_information_dict['offererId'] = offerer.id
                bank_information_dict['idAtProviders'] = siren
        elif bank_information_dict['ribAffiliation'] == "Le RIB lié à un unique SIRET":
            siret = application_details['dossier']['etablissement']['siret']
            venue = venue_queries.find_by_siret(siret)
            if venue:
                bank_information_dict['venueId'] = venue.id
                bank_information_dict['idAtProviders'] = siret
        else:
            self.logEvent(LocalProviderEventType.SyncError,
                          f'unknown RIB affiliation for application id {self.application_id}')
            raise UnknownRibAffiliation
        return bank_information_dict


def _find_value_in_fields(fields, value_name):
    for field in fields:
        if field["type_de_champ"]["libelle"] == value_name:
            return field["value"]
