import os
from datetime import datetime
from typing import List, Optional
from typing import Dict

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
from sqlalchemy.orm.exc import MultipleResultsFound
from domain.bank_information import check_offerer_presence, check_venue_presence, check_venue_queried_by_name, VenueMatchingError


class VenueBankInformationProvider(LocalProvider):
    name = "Demarches simplifiees / Venue Bank Information"
    can_create = True
    FIELD_FOR_VENUE_WITH_SIRET = "Si vous souhaitez renseigner les coordonn\u00e9es bancaires d'un lieu avec SIRET, merci de saisir son SIRET :"
    FIELD_FOR_VENUE_WITHOUT_SIRET = "Si vous souhaitez renseigner les coordonn\u00e9es bancaires d'un lieu sans SIRET, merci de saisir le \"Nom du lieu\", \u00e0 l'identique de celui dans le pass Culture Pro :"

    def __init__(self, minimum_requested_datetime: datetime = datetime.utcnow()):
        super().__init__()
        self.PROCEDURE_ID = os.environ.get(
            'DEMARCHES_SIMPLIFIEES_RIB_VENUE_PROCEDURE_ID', None)
        self.TOKEN = os.environ.get('DEMARCHES_SIMPLIFIEES_TOKEN', None)

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
        bank_information.venueId = self.bank_information_dict.get(
            'venueId', None)

    def retrieve_bank_information(self, application_details: Dict) -> Optional[Dict]:
        bank_information_dict = dict()
        bank_information_dict['lastUpdate'] = application_details['dossier']['updated_at']
        bank_information_dict['iban'] = _find_value_in_fields(
            application_details['dossier']["champs"], "IBAN")
        bank_information_dict['bic'] = _find_value_in_fields(
            application_details['dossier']["champs"], "BIC")
        bank_information_dict['applicationId'] = application_details['dossier']["id"]
        siren = application_details['dossier']['entreprise']['siren']

        try:
            offerer = offerer_queries.find_by_siren(siren)
            check_offerer_presence(offerer)

            siret = _find_value_in_fields(
                application_details['dossier']["champs"], self.FIELD_FOR_VENUE_WITH_SIRET)
            if siret:
                venue = venue_queries.find_by_managing_offerer_id_and_siret(
                    offerer.id, siret)
                check_venue_presence(venue)

            else:
                name = _find_value_in_fields(
                    application_details['dossier']["champs"], self.FIELD_FOR_VENUE_WITHOUT_SIRET)
                venues = venue_queries.find_venue_without_siret_by_managing_offerer_id_and_name(
                    offerer.id, name)
                check_venue_queried_by_name(venues)
                venue = venues[0]

            bank_information_dict['venueId'] = venue.id
            bank_information_dict['idAtProviders'] = _compute_id_at_provider(
                venue, offerer)

        except VenueMatchingError as err:
            self.log_provider_event(LocalProviderEventType.SyncError,
                                    f"{err} for application id {bank_information_dict['applicationId']}")
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


def _compute_id_at_provider(venue, offerer) -> str:
    if (venue.siret):
        return venue.siret
    return f'{offerer.siren}{venue.name}'
