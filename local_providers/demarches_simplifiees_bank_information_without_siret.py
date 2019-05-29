import os
from datetime import datetime
from pprint import pprint

from connectors.api_demarches_simplifiees import get_application_details
from domain.bank_account import get_all_application_ids_from_demarches_simplifiees_procedure, format_raw_iban_or_bic
from models import LocalProvider, BankInformation, Offerer, Venue
from models.local_provider import ProvidableInfo
from repository.local_provider_event_queries import find_latest_sync_end_event
from utils.date import DATE_ISO_FORMAT
from utils.human_ids import dehumanize


class NoOffererFoundException(Exception):
    pass


class NoVenueFoundException(Exception):
    pass


class VenueWithoutSIRETBankInformationProvider(LocalProvider):
    help = ""
    identifierDescription = ""
    identifierRegexp = None
    name = "Demarches simplifiees / IBAN for venue without SIRET"
    objectType = BankInformation
    canCreate = True

    def __init__(self):
        super().__init__()
        self.PROCEDURE_ID = os.environ['DEMARCHES_SIMPLIFIEES_PROCEDURE_ID_VENUE_WITHOUT_SIRET']
        self.TOKEN = os.environ['DEMARCHES_SIMPLIFIEES_TOKEN']

        last_sync_event = find_latest_sync_end_event(self.dbObject)

        if last_sync_event:
            last_sync_date = last_sync_event.date
        else:
            last_sync_date = datetime(1970, 1, 1)

        self.application_ids = iter(
            get_all_application_ids_from_demarches_simplifiees_procedure(self.PROCEDURE_ID, self.TOKEN, last_sync_date)
        )

    def __next__(self) -> ProvidableInfo:
        self.application_id = next(self.application_ids)

        pprint('TOTO')

        application_response = get_application_details(self.application_id, self.PROCEDURE_ID, self.TOKEN)
        self.application_details = DemarchesSimplifieesMapper.from_venue_without_SIRET_application(application_response)

        offerer = Offerer.query.filter_by(id=self.application_details['structureId']).first()

        if offerer is None:
            raise NoOffererFoundException

        venue = Venue.query.filter_by(id=self.application_details['venueId']).first()

        if venue is None:
            raise NoVenueFoundException

        return self.retrieve_providable_info()

    def retrieve_providable_info(self) -> ProvidableInfo:
        providable_info = ProvidableInfo()
        providable_info.idAtProviders = \
            f"{self.application_details['structureId']}|{self.application_details['venueId']}"

        providable_info.type = BankInformation
        providable_info.dateModifiedAtProvider = self.application_details['updated_at']
        return providable_info

    def updateObject(self, bank_information):
        bank_information.iban = format_raw_iban_or_bic(self.application_details['IBAN'])
        bank_information.bic = format_raw_iban_or_bic(self.application_details['BIC'])
        bank_information.applicationId = self.application_details['applicationId']
        bank_information.offererId = self.application_details.get('structureId', None)
        bank_information.venueId = self.application_details.get('venueId', None)


class DemarchesSimplifieesMapper:
    def _find_value_in_fields(fields, value_name):
        for field in fields:
            if field["type_de_champ"]["libelle"] == value_name:
                return field["value"]

    @classmethod
    def from_venue_without_SIRET_application(cls, response) -> dict:
        application_details = dict()
        application_details['BIC'] = cls._find_value_in_fields(response['dossier']["champs"], "BIC")
        application_details['IBAN'] = cls._find_value_in_fields(response['dossier']["champs"], "IBAN")
        application_details['applicationId'] = response['dossier']["id"]
        application_details['updated_at'] = datetime.strptime(response['dossier']["updated_at"], DATE_ISO_FORMAT)

        url = cls._find_value_in_fields(response['dossier']["champs"], "URL")
        human_structure_id = url.split('/')[-3]
        human_venue_id = url.split('/')[-1]

        application_details['structureId'] = dehumanize(human_structure_id)
        application_details['venueId'] = dehumanize(human_venue_id)

        return application_details
