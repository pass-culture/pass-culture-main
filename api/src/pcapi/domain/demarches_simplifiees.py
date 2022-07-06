from datetime import datetime
import logging
from typing import Optional

from pcapi import settings
from pcapi.connectors.dms import api as api_dms
from pcapi.connectors.dms import models as dms_models
from pcapi.core.finance.models import BankInformationStatus
from pcapi.core.finance.utils import format_raw_iban_and_bic
from pcapi.domain.bank_information import CannotRegisterBankInformation
from pcapi.utils.date import DATE_ISO_FORMAT


logger = logging.getLogger(__name__)


FIELD_FOR_VENUE_WITH_SIRET = (
    "Si vous souhaitez renseigner les coordonn\u00e9es bancaires d'un lieu avec SIRET, merci de saisir son SIRET :"
)
FIELD_FOR_VENUE_WITHOUT_SIRET = "Si vous souhaitez renseigner les coordonn\u00e9es bancaires d'un lieu sans SIRET, merci de saisir le \"Nom du lieu\", \u00e0 l'identique de celui dans le pass Culture Pro :"

ACCEPTED_DMS_STATUS = (dms_models.DmsApplicationStates.closed,)
DRAFT_DMS_STATUS = (
    dms_models.DmsApplicationStates.received,
    dms_models.DmsApplicationStates.initiated,
)
REJECTED_DMS_STATUS = (
    dms_models.DmsApplicationStates.refused,
    dms_models.DmsApplicationStates.without_continuation,
)


class ApplicationDetail:
    def __init__(
        self,
        siren: str,
        status: BankInformationStatus,
        application_id: int,
        iban: str,
        bic: str,
        modification_date: datetime,
        siret: Optional[str] = None,
        venue_name: Optional[str] = None,
        annotation_id: Optional[str] = None,
        dossier_id: str = None,
    ):
        self.siren = siren
        self.status = status
        self.application_id = application_id
        self.iban = format_raw_iban_and_bic(iban)
        self.bic = format_raw_iban_and_bic(bic)
        self.siret = siret
        self.venue_name = venue_name
        self.modification_date = modification_date
        self.annotation_id = annotation_id
        self.dossier_id = dossier_id


def parse_raw_bic_data(data: dict) -> dict:
    result = {
        "status": data["dossier"]["state"],
        "updated_at": data["dossier"]["dateDerniereModification"],
        "dossier_id": data["dossier"]["id"],
    }
    ID_TO_NAME_MAPPING = {
        "Q2hhbXAtNDA3ODg5": "firstname",
        "Q2hhbXAtNDA3ODkw": "lastname",
        "Q2hhbXAtNDA3ODky": "phone_number",
        "Q2hhbXAtMzUyNzIy": "iban",
        "Q2hhbXAtMzUyNzI3": "bic",
    }
    for field in data["dossier"]["champs"]:
        if field["id"] in ID_TO_NAME_MAPPING:
            result[ID_TO_NAME_MAPPING[field["id"]]] = field["value"]
        elif field["id"] == "Q2hhbXAtNzgyODAw":
            result["siret"] = field["etablissement"]["siret"]
            result["siren"] = field["etablissement"]["siret"][:9]

    result["annotation_id"] = None
    for annotation in data["dossier"]["annotations"]:
        if annotation["label"] == "Erreur traitement pass Culture":
            result["annotation_id"] = annotation["id"]
            break
    return result


def get_venue_bank_information_application_details_by_application_id(
    application_id: str, version: int = 1
) -> ApplicationDetail:
    if version == 1:
        assert settings.DMS_VENUE_PROCEDURE_ID
        assert settings.DMS_TOKEN
        response_application_details = api_dms.get_application_details(
            application_id, procedure_id=settings.DMS_VENUE_PROCEDURE_ID, token=settings.DMS_TOKEN
        )

        application_details = ApplicationDetail(
            siren=response_application_details["dossier"]["entreprise"]["siren"],
            status=_get_status_from_demarches_simplifiees_application_state(
                response_application_details["dossier"]["state"]
            ),
            application_id=int(response_application_details["dossier"]["id"]),
            iban=format_raw_iban_and_bic(  # type: ignore [arg-type]
                _find_value_in_fields(response_application_details["dossier"]["champs"], "IBAN")  # type: ignore [arg-type]
            ),
            bic=format_raw_iban_and_bic(  # type: ignore [arg-type]
                _find_value_in_fields(response_application_details["dossier"]["champs"], "BIC")  # type: ignore [arg-type]
            ),
            siret=_find_value_in_fields(response_application_details["dossier"]["champs"], FIELD_FOR_VENUE_WITH_SIRET),  # type: ignore [arg-type]
            venue_name=_find_value_in_fields(  # type: ignore [arg-type]
                response_application_details["dossier"]["champs"], FIELD_FOR_VENUE_WITHOUT_SIRET
            ),
            modification_date=datetime.strptime(response_application_details["dossier"]["updated_at"], DATE_ISO_FORMAT),
        )
        return application_details
    if version == 2:
        client = api_dms.DMSGraphQLClient()
        raw_data = client.get_bic(int(application_id))
        data = parse_raw_bic_data(raw_data)
        return ApplicationDetail(
            siren=data["siren"],
            status=_get_status_from_demarches_simplifiees_application_state_v2(
                dms_models.GraphQLApplicationStates(data["status"])
            ),
            application_id=int(application_id),
            iban=data["iban"],
            bic=data["bic"],
            siret=data["siret"],
            modification_date=datetime.fromisoformat(data["updated_at"]).astimezone().replace(tzinfo=None),
            annotation_id=data["annotation_id"],
            dossier_id=data["dossier_id"],
        )
    raise ValueError("Unknown version %s" % version)


def _get_status_from_demarches_simplifiees_application_state(state: str) -> BankInformationStatus:
    try:
        dms_state = dms_models.DmsApplicationStates[state]
    except KeyError:
        raise CannotRegisterBankInformation(errors={"BankInformation": f"Unknown Demarches Simplifiées state {state}"})
    rejected_states = REJECTED_DMS_STATUS
    accepted_states = ACCEPTED_DMS_STATUS
    draft_states = DRAFT_DMS_STATUS
    if dms_state in rejected_states:
        return BankInformationStatus.REJECTED
    if dms_state in accepted_states:
        return BankInformationStatus.ACCEPTED
    if dms_state in draft_states:
        return BankInformationStatus.DRAFT
    raise ValueError(f"Unexpected DMS status: '{state}'")


def _get_status_from_demarches_simplifiees_application_state_v2(
    state: dms_models.GraphQLApplicationStates,
) -> BankInformationStatus:
    return {
        dms_models.GraphQLApplicationStates.draft: BankInformationStatus.DRAFT,
        dms_models.GraphQLApplicationStates.on_going: BankInformationStatus.DRAFT,
        dms_models.GraphQLApplicationStates.accepted: BankInformationStatus.ACCEPTED,
        dms_models.GraphQLApplicationStates.refused: BankInformationStatus.REJECTED,
        dms_models.GraphQLApplicationStates.without_continuation: BankInformationStatus.REJECTED,
    }[state]


def _find_value_in_fields(fields: list[dict], value_name: str) -> Optional[dict]:
    for field in fields:
        if field["type_de_champ"]["libelle"] == value_name:
            return field["value"]
    return None


def update_demarches_simplifiees_text_annotations(dossier_id: str, annotation_id: str, message: str) -> None:
    client = api_dms.DMSGraphQLClient()
    client.update_text_annotation(dossier_id, settings.DMS_INSTRUCTOR_ID, annotation_id, message)


def archive_dossier(dossier_id: str) -> None:
    client = api_dms.DMSGraphQLClient()
    client.archive_application(dossier_id, settings.DMS_INSTRUCTOR_ID)


def format_error_to_demarches_simplifiees_text(api_error: CannotRegisterBankInformation) -> str:
    error_fields = []
    for key, value in api_error.errors.items():
        error_fields.append("%s: %s" % (key, ", ".join(value)))
    return "; ".join(error_fields)
