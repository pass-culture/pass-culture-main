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

        self.application_ids = iter(get_all_application_ids_from_demarches_simplifiees_procedure())
        self.application_details = None
        self.application_id = None

    def __next__(self):
        self.application_details = None

        self.application_id = self.application_ids.__next__()

        if self.application_details is None:
            self.get_next_application_details()

        if not self.application_details:
            return None

        self.siren = self.application_details['dossier']['entreprise']['siren']
        self.siret = self.application_details['dossier']['etablissement']['siret']
        self.offerer = offerer_queries.find_by_siren(self.siren)
        self.venue = venue_queries.find_by_siret(self.siret)

        providable_info = ProvidableInfo()
        providable_info.type = BankInformation
        rib_affiliation = _find_value_in_fields(self.application_details['dossier']["champs"],
                                        "Je souhaite renseigner")
        if rib_affiliation  == "Le RIB par défaut pour toute structure liée à mon SIREN":
            providable_info.idAtProviders = self.siren
        elif rib_affiliation == "Le RIB lié à un unique SIRET":
            providable_info.idAtProviders = self.siret
        else:
            self.logEvent(LocalProviderEventType.SyncError, f'unknown RIB affiliation for application id {self.application_id}')
            return None
        
        providable_info.dateModifiedAtProvider = datetime.strptime(self.application_details['dossier']['updated_at'], DATE_ISO_FORMAT)

        return providable_info

    def get_next_application_details(self):
        if self.application_id:
            self.logEvent(LocalProviderEventType.SyncPartEnd, self.application_id)

        self.logEvent(LocalProviderEventType.SyncPartStart, self.application_id)
        self.application_details = get_application_details(self.application_id)

    def updateObject(self, bank_information):

        assert bank_information.idAtProviders == self.siren or bank_information.idAtProviders == self.siret

        bank_information.iban = _find_value_in_fields(self.application_details['dossier']["champs"], "IBAN")
        bank_information.bic = _find_value_in_fields(self.application_details['dossier']["champs"], "BIC")
        bank_information.application_id = self.application_details['dossier']["id"]
        bank_information.offerer = self.offerer
        bank_information.venue = self.venue


def _find_value_in_fields(fields, value_name):
    for field in fields:
        if field["type_de_champ"]["libelle"] == value_name:
            return field["value"]
