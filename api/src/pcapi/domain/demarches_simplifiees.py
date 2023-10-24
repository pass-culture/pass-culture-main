from datetime import datetime
import logging

from pcapi import settings
from pcapi.connectors.dms import api as api_dms
from pcapi.connectors.dms import models as dms_models
from pcapi.core.finance.models import BankInformationStatus
from pcapi.core.finance.utils import format_raw_iban_and_bic
from pcapi.domain.bank_information import CannotRegisterBankInformation


logger = logging.getLogger(__name__)

FIELD_NAME_TO_INTERNAL_NAME_MAPPING = {
    ("Prénom", "prénom"): "firstname",
    ("Nom", "nom"): "lastname",
    ("Mon numéro de téléphone",): "phone_number",
    ("IBAN",): "iban",
    ("BIC",): "bic",
}
DMS_TOKEN_ID = "Q2hhbXAtMjY3NDMyMQ=="
ACCEPTED_DMS_STATUS = (dms_models.DmsApplicationStates.closed,)
DRAFT_DMS_STATUS = (
    dms_models.DmsApplicationStates.received,
    dms_models.DmsApplicationStates.initiated,
)
REJECTED_DMS_STATUS = (
    dms_models.DmsApplicationStates.refused,
    dms_models.DmsApplicationStates.without_continuation,
)
DMS_TOKEN_PRO_PREFIX = "PRO-"


class ApplicationDetail:
    def __init__(
        self,
        status: BankInformationStatus,
        application_id: int,
        modification_date: datetime,
        siren: str | None = None,
        iban: str | None = None,
        bic: str | None = None,
        siret: str | None = None,
        venue_name: str | None = None,
        dms_token: str | None = None,
        error_annotation_id: str | None = None,
        venue_url_annotation_id: str | None = None,
        dossier_id: str | None = None,
    ):
        self.siren = siren
        self.status = status
        self.application_id = application_id
        self.iban = format_raw_iban_and_bic(iban)
        self.bic = format_raw_iban_and_bic(bic)
        self.siret = siret
        self.venue_name = venue_name
        self.dms_token = dms_token
        self.modification_date = modification_date
        self.error_annotation_id = error_annotation_id
        self.venue_url_annotation_id = venue_url_annotation_id
        self.dossier_id = dossier_id


def parse_raw_bank_info_data(data: dict, procedure_version: int) -> dict:
    result = {
        "status": data["dossier"]["state"],
        "updated_at": data["dossier"]["dateDerniereModification"],
        "dossier_id": data["dossier"]["id"],
    }
    for field in data["dossier"]["champs"]:
        for mapped_fields, internal_field in FIELD_NAME_TO_INTERNAL_NAME_MAPPING.items():
            if field["label"] in mapped_fields:
                result[internal_field] = field["value"]
            elif field["id"] == DMS_TOKEN_ID:
                result["dms_token"] = _remove_dms_pro_prefix(field["value"].strip("  "))
            elif field["id"] == "Q2hhbXAtNzgyODAw" and procedure_version in (2, 3):
                result["siret"] = field["etablissement"]["siret"]
                result["siren"] = field["etablissement"]["siret"][:9]

    result["error_annotation_id"] = None
    result["venue_url_annotation_id"] = None
    for annotation in data["dossier"]["annotations"]:
        match annotation["label"]:
            case "Erreur traitement pass Culture":
                result["error_annotation_id"] = annotation["id"]
            case "URL du lieu":
                result["venue_url_annotation_id"] = annotation["id"]
    return result


def _remove_dms_pro_prefix(dms_token: str) -> str:
    if dms_token.startswith(DMS_TOKEN_PRO_PREFIX):
        return dms_token[len(DMS_TOKEN_PRO_PREFIX) :]
    return dms_token


def get_venue_bank_information_application_details_by_application_id(
    application_id: str,
    procedure_version: int = 4,
) -> ApplicationDetail:
    client = api_dms.DMSGraphQLClient()
    raw_data = client.get_bank_info(int(application_id))
    data = parse_raw_bank_info_data(raw_data, procedure_version)
    return ApplicationDetail(
        siren=data.get("siren", None),
        status=_get_status_from_demarches_simplifiees_application_state_v2(
            dms_models.GraphQLApplicationStates(data["status"])
        ),
        application_id=int(application_id),
        iban=data["iban"],
        bic=data["bic"],
        siret=data.get("siret", None),
        dms_token=data["dms_token"] if procedure_version == 4 else None,
        modification_date=datetime.fromisoformat(data["updated_at"]).astimezone().replace(tzinfo=None),
        error_annotation_id=data["error_annotation_id"],
        dossier_id=data["dossier_id"],
        venue_url_annotation_id=data["venue_url_annotation_id"],
    )


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


def update_demarches_simplifiees_text_annotations(dossier_id: str, annotation_id: str, message: str) -> None:
    client = api_dms.DMSGraphQLClient()
    result = client.update_text_annotation(dossier_id, settings.DMS_INSTRUCTOR_ID, annotation_id, message)
    errors = result["dossierModifierAnnotationText"].get("errors")  # pylint: disable=unsubscriptable-object
    if errors:
        logger.error(
            "Got error when updating DMS annotation",
            extra={
                "errors": errors,
                "dossier": dossier_id,
            },
        )


def archive_dossier(dossier_id: str) -> None:
    client = api_dms.DMSGraphQLClient()
    client.archive_application(dossier_id, settings.DMS_INSTRUCTOR_ID)


def format_error_to_demarches_simplifiees_text(api_error: CannotRegisterBankInformation) -> str:
    error_fields = []
    for key, value in api_error.errors.items():
        error_fields.append("%s: %s" % (key, ", ".join(value)))
    return "; ".join(error_fields)
