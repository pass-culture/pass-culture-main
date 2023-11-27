import logging

from pcapi import settings
from pcapi.connectors.dms import api as api_dms
from pcapi.connectors.dms import models as dms_models
from pcapi.core.finance.models import BankInformationStatus
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


def parse_raw_bank_info_data(data: dict, procedure_version: int) -> dict:
    result = {
        "status": data["state"],
        "updated_at": data["dateDerniereModification"],
        "dossier_id": data["id"],
        "application_id": data["number"],
    }

    result["error_annotation_id"] = None
    result["venue_url_annotation_id"] = None
    for annotation in data["annotations"]:
        match annotation["label"]:
            case "Erreur traitement pass Culture" | "Annotation technique (réservée à pcapi)":
                result["error_annotation_id"] = annotation["id"]
                result["error_annotation_value"] = annotation["stringValue"]
            case "URL du lieu":
                result["venue_url_annotation_id"] = annotation["id"]

    match procedure_version:
        case 2 | 3:
            _parse_v2_v3_content(data, result)
        case 4:
            _parse_v4_content(data, result)
        case 5:
            _parse_v5_content(data, result)

    return result


def _parse_v2_v3_content(data: dict, result: dict) -> dict:
    for field in data["champs"]:
        for mapped_fields, internal_field in FIELD_NAME_TO_INTERNAL_NAME_MAPPING.items():
            if field["label"] in mapped_fields:
                result[internal_field] = field["value"]
            elif field["id"] == DMS_TOKEN_ID:
                result["dms_token"] = _remove_dms_pro_prefix(field["value"].strip("  "))
            elif field["id"] == "Q2hhbXAtNzgyODAw":
                result["siret"] = field["etablissement"]["siret"]
                result["siren"] = field["etablissement"]["siret"][:9]
    return result


def _parse_v4_content(data: dict, result: dict) -> dict:
    for field in data["champs"]:
        for mapped_fields, internal_field in FIELD_NAME_TO_INTERNAL_NAME_MAPPING.items():
            if field["label"] in mapped_fields:
                result[internal_field] = field["value"]
            elif field["id"] == DMS_TOKEN_ID:
                result["dms_token"] = _remove_dms_pro_prefix(field["value"].strip("  "))
    return result


def _parse_v5_content(data: dict, result: dict) -> dict:
    for field in data["champs"]:
        for mapped_fields, internal_field in FIELD_NAME_TO_INTERNAL_NAME_MAPPING.items():
            if field["label"] in mapped_fields:
                result[internal_field] = field["value"]
    result["siret"] = data["demandeur"]["siret"]
    result["siren"] = result["siret"][:9]

    return result


def _remove_dms_pro_prefix(dms_token: str) -> str:
    if dms_token.startswith(DMS_TOKEN_PRO_PREFIX):
        return dms_token[len(DMS_TOKEN_PRO_PREFIX) :]
    return dms_token


def get_status_from_demarches_simplifiees_application_state_v2(
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
