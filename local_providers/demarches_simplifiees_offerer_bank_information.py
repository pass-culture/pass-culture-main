import os
from datetime import datetime
from typing import List, Optional

from connectors.api_demarches_simplifiees import get_application_details
from domain.bank_account import format_raw_iban_or_bic
from domain.demarches_simplifiees import get_closed_application_ids_for_demarche_simplifiee
from local_providers.local_provider import LocalProvider
from local_providers.providable_info import ProvidableInfo
from models import BankInformation
from models.local_provider_event import LocalProviderEventType
from repository import offerer_queries, venue_queries
from repository.bank_information_queries import get_last_update_from_bank_information
from utils.date import DATE_ISO_FORMAT


class OffererBankInformationProvider(LocalProvider):
    name = "Demarches simplifiees / Offerer Bank Information"
    can_create = True

    def __init__(self, minimum_requested_datetime: datetime = datetime.utcnow()):
        super().__init__()
        self.PROCEDURE_ID = os.environ.get(
            'DEMARCHES_SIMPLIFIEES_RIB_OFFERER_PROCEDURE_ID')
        self.TOKEN = os.environ.get('DEMARCHES_SIMPLIFIEES_TOKEN')

        most_recent_known_application_date = get_last_update_from_bank_information(
            last_provider_id=self.provider.id)
        requested_datetime = min(
            minimum_requested_datetime, most_recent_known_application_date)

        self.application_ids = iter(
            get_closed_application_ids_for_demarche_simplifiee(self.PROCEDURE_ID, self.TOKEN,
                                                               requested_datetime))

    def __next__(self) -> List[ProvidableInfo]:
        self.bank_information_dict = self.retrieve_next_bank_information()

        if not self.bank_information_dict:
            return []

        bank_information_last_update = datetime.strptime(
            self.bank_information_dict['lastUpdate'], DATE_ISO_FORMAT)
        bank_information_identifier = self.bank_information_dict['idAtProviders']
        bank_information_providable_info = self.create_providable_info(BankInformation,
                                                                       bank_information_identifier,
                                                                       bank_information_last_update)
        return [bank_information_providable_info]

    def fill_object_attributes(self, bank_information: BankInformation):
        bank_information.iban = format_raw_iban_or_bic(
            self.bank_information_dict['iban'])
        bank_information.bic = format_raw_iban_or_bic(
            self.bank_information_dict['bic'])
        bank_information.applicationId = self.bank_information_dict['applicationId']
        bank_information.offererId = self.bank_information_dict.get(
            'offererId', None)

    def retrieve_bank_information(self, application_details: dict) -> Optional[dict]:
        bank_information_dict = dict()
        bank_information_dict['lastUpdate'] = application_details['dossier']['updated_at']
        bank_information_dict['iban'] = _find_value_in_fields(
            application_details['dossier']["champs"], "IBAN")
        bank_information_dict['bic'] = _find_value_in_fields(
            application_details['dossier']["champs"], "BIC")
        bank_information_dict['applicationId'] = application_details['dossier']["id"]

        siren = application_details['dossier']['entreprise']['siren']
        offerer = offerer_queries.find_by_siren(siren)
        if offerer:
            bank_information_dict['offererId'] = offerer.id
            bank_information_dict['idAtProviders'] = siren

        if 'idAtProviders' not in bank_information_dict:
            self.log_provider_event(LocalProviderEventType.SyncError,
                                    f"unknown siren for application id"
                                    f" {bank_information_dict['applicationId']}")
            return {}

        return bank_information_dict

    def retrieve_next_bank_information(self) -> dict:
        application_id = next(self.application_ids)
        application_details = get_application_details(
            application_id, self.PROCEDURE_ID, self.TOKEN)
        return self.retrieve_bank_information(application_details)


def _find_value_in_fields(fields, value_name):
    for field in fields:
        if field["type_de_champ"]["libelle"] == value_name:
            return field["value"]
