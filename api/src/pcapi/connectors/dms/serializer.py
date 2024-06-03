from datetime import datetime
from datetime import timedelta
import logging
import re
from textwrap import shorten
from typing import Any
from typing import Literal

from dateutil import parser as date_parser
from pydantic.v1 import Field
from pydantic.v1 import root_validator
from pydantic.v1 import validator

from pcapi import settings
from pcapi.connectors.dms import models as dms_models
from pcapi.core.finance import models as finance_models
from pcapi.core.finance.api import mark_bank_account_without_continuation
from pcapi.core.finance.utils import format_raw_iban_and_bic
from pcapi.core.fraud import api as fraud_api
from pcapi.core.fraud import models as fraud_models
from pcapi.core.users import models as users_models
from pcapi.routes.serialization import BaseModel
from pcapi.serialization.utils import without_timezone
from pcapi.utils.date import FrenchParserInfo


logger = logging.getLogger(__name__)


DMS_ACTIVITY_ENUM_MAPPING = {
    "Collégien": users_models.ActivityEnum.MIDDLE_SCHOOL_STUDENT.value,
    "Lycéen": users_models.ActivityEnum.HIGH_SCHOOL_STUDENT.value,
    "Étudiant": users_models.ActivityEnum.STUDENT.value,
    "Etudiant": users_models.ActivityEnum.STUDENT.value,
    "Employé": users_models.ActivityEnum.EMPLOYEE.value,
    "En recherche d'emploi ou chômeur": users_models.ActivityEnum.UNEMPLOYED.value,
    "Chômeur, En recherche d'emploi": users_models.ActivityEnum.UNEMPLOYED.value,
    "Inactif (ni en emploi ni au chômage), En incapacité de travailler": users_models.ActivityEnum.INACTIVE.value,
    "Apprenti": users_models.ActivityEnum.APPRENTICE.value,
    "Alternant": users_models.ActivityEnum.APPRENTICE_STUDENT.value,
    "Volontaire en service civique rémunéré": users_models.ActivityEnum.VOLUNTEER.value,
}

DMS_ANNOTATION_SLUG = "AN_001"


def _sanitize_id_piece_number(id_piece_number: str) -> str:
    """
    Replaces double spaces by single spaces.
    This is to avoid errors when parsing the ID piece number.
    """
    return re.sub(" +", " ", id_piece_number)


def parse_beneficiary_information_graphql(
    application_detail: dms_models.DmsApplicationResponse,
) -> fraud_models.DMSContent:
    application_number = application_detail.number
    civility = application_detail.applicant.civility
    email = application_detail.applicant.email or application_detail.profile.email
    first_name = application_detail.applicant.first_name
    last_name = application_detail.applicant.last_name
    registration_datetime = application_detail.draft_date
    processed_datetime = application_detail.processed_datetime

    # Fields that may be filled
    activity = None
    address = None
    birth_date = None
    city = None
    department = None
    id_piece_number = None
    phone = None
    postal_code = None
    annotation = None

    field_errors: list[fraud_models.DmsFieldErrorDetails] = []

    if not fraud_api.is_subscription_name_valid(first_name):
        field_errors.append(
            fraud_models.DmsFieldErrorDetails(key=fraud_models.DmsFieldErrorKeyEnum.first_name, value=first_name)
        )

    if not fraud_api.is_subscription_name_valid(last_name):
        field_errors.append(
            fraud_models.DmsFieldErrorDetails(key=fraud_models.DmsFieldErrorKeyEnum.last_name, value=last_name)
        )

    for field in application_detail.fields:
        label = field.label.lower()
        value = field.value or ""

        if dms_models.FieldLabelKeyword.ACTIVITY.value in label:
            activity = DMS_ACTIVITY_ENUM_MAPPING.get(value) if value else None
            if activity is None:
                logger.error("Unknown activity value for application %s: %s", application_number, value)

        elif dms_models.FieldLabelKeyword.ADDRESS.value in label:
            address = value

        elif dms_models.FieldLabelKeyword.BIRTH_DATE.value in label:
            try:
                birth_date = date_parser.parse(value, FrenchParserInfo())
            except date_parser.ParserError:
                field_errors.append(
                    fraud_models.DmsFieldErrorDetails(key=fraud_models.DmsFieldErrorKeyEnum.birth_date, value=value)
                )
                logger.error("Could not parse birth date %s for DMS application %s", value, application_number)

        elif dms_models.FieldLabelKeyword.ID_PIECE_NUMBER.value in label:
            value = _sanitize_id_piece_number(value.strip())
            if not fraud_api.validate_id_piece_number_format_fraud_item(value, application_detail.procedure.number):
                field_errors.append(
                    fraud_models.DmsFieldErrorDetails(
                        key=fraud_models.DmsFieldErrorKeyEnum.id_piece_number, value=value
                    )
                )
            else:
                id_piece_number = value

        elif dms_models.FieldLabelKeyword.TELEPHONE.value in label:
            phone = value.replace(" ", "")

        # The order between POSTAL_CODE and CITY check is important. Postal code needs to happen first.
        # If we check CITY first, we will get a false positive for the postal code,
        # because both labels match the 'commune de résidence' keyword
        elif dms_models.FieldLabelKeyword.POSTAL_CODE.value in label:
            space_free_value = str(value).strip().replace(" ", "")
            match = re.search("^[0-9]{5}", space_free_value)
            if match is None:
                field_errors.append(
                    fraud_models.DmsFieldErrorDetails(key=fraud_models.DmsFieldErrorKeyEnum.postal_code, value=value)
                )
                continue
            postal_code = match.group(0)

        elif dms_models.FieldLabelKeyword.CITY_1.value in label or dms_models.FieldLabelKeyword.CITY_2.value in label:
            city = value

    for remote_annotation in application_detail.annotations:
        if DMS_ANNOTATION_SLUG in remote_annotation.label:
            annotation = fraud_models.DmsAnnotation(
                id=remote_annotation.id, label=remote_annotation.label, text=remote_annotation.value
            )
            break

    return fraud_models.DMSContent(  # type: ignore[call-arg]
        activity=activity,
        address=address,
        annotation=annotation,
        application_number=application_number,
        birth_date=birth_date,
        city=city,
        civility=_parse_dms_civility(civility),
        department=department,
        email=email,
        field_errors=field_errors,
        first_name=first_name,
        id_piece_number=id_piece_number,
        last_name=last_name,
        latest_modification_datetime=application_detail.latest_modification_datetime,
        phone=phone,
        postal_code=postal_code,
        procedure_number=application_detail.procedure.number,
        processed_datetime=processed_datetime,
        registration_datetime=registration_datetime,
        state=application_detail.state.value,
    )


def _parse_dms_civility(civility: dms_models.Civility) -> users_models.GenderEnum | None:
    if civility == dms_models.Civility.M:
        return users_models.GenderEnum.M
    if civility == dms_models.Civility.MME:
        return users_models.GenderEnum.F
    return None


class ApplicationDetail(BaseModel):
    procedure_version: int
    application_id: int
    dossier_id: str
    modification_date: datetime
    siren: str | None = None
    iban: str
    obfuscatedIban: str
    bic: str
    siret: str | None = None
    dms_token: str | None = None
    error_annotation_id: str
    error_annotation_value: str | None = None
    venue_url_annotation_id: str | None = None
    venue_url_annotation_value: str | None = None
    status: finance_models.BankAccountApplicationStatus
    label: str | None = None

    @validator("label")
    def truncate_label(cls: "ApplicationDetail", label: str) -> str:
        return shorten(label, width=100, placeholder="...")

    @property
    def is_accepted(self) -> bool:
        return self.status == finance_models.BankAccountApplicationStatus.ACCEPTED

    @property
    def is_refused(self) -> bool:
        return self.status == finance_models.BankAccountApplicationStatus.REFUSED

    @root_validator(pre=True)
    def to_representation(cls: "ApplicationDetail", obj: dict) -> dict:
        to_representation: dict[str, Any] = {}
        to_representation["procedure_version"] = obj["application_type"]
        to_representation["application_id"] = obj["application_id"]
        to_representation["dossier_id"] = obj["dossier_id"]
        to_representation["siren"] = obj.get("siren")
        to_representation["iban"] = format_raw_iban_and_bic(obj["iban"])
        to_representation["obfuscatedIban"] = f"""XXXX XXXX XXXX {to_representation["iban"][-4:]}"""
        to_representation["bic"] = format_raw_iban_and_bic(obj["bic"])
        to_representation["dms_token"] = obj.get("dms_token") if obj.get("application_type") == 4 else None
        to_representation["modification_date"] = (
            datetime.fromisoformat(obj["updated_at"]).astimezone().replace(tzinfo=None)
        )
        to_representation["error_annotation_id"] = obj["error_annotation_id"]
        to_representation["error_annotation_value"] = obj.get("error_annotation_value")
        to_representation["venue_url_annotation_id"] = obj["venue_url_annotation_id"]
        to_representation["venue_url_annotation_value"] = obj.get("venue_url_annotation_value")
        to_representation["status"] = finance_models.BankAccountApplicationStatus(obj["status"])
        if (
            to_representation["status"] == finance_models.BankAccountApplicationStatus.DRAFT
            and obj["last_pending_correction_date"]
        ):
            to_representation["status"] = finance_models.BankAccountApplicationStatus.WITH_PENDING_CORRECTIONS
        if to_representation["procedure_version"] == 5:
            to_representation["siret"] = obj["siret"]
            to_representation["siren"] = to_representation["siret"][:9]
            to_representation["label"] = obj["label"]

        return to_representation


class Annotation(BaseModel):
    """
    BaseModel for DS application annotations
    """

    id: str
    label: str
    updated_at: datetime = Field(alias="updatedAt")
    string_value: str = Field(alias="stringValue")

    @validator("updated_at", pre=False)
    def strip_timezone(cls, value: datetime) -> datetime:
        return without_timezone(value)


class FieldAnnotation(Annotation):
    """
    Text field annotation
    """


class CheckBoxAnnotation(Annotation):
    """
    Checkbox annotation
    """

    checked: bool


class ProcessingErrorPassCulture(FieldAnnotation):
    label: Literal["Erreur traitement pass Culture"]

    @validator("string_value")
    def lower_string_value(cls, string_value: str) -> str:
        return string_value.lower()


class WaitingForOffererValidation(CheckBoxAnnotation):
    label: Literal["En attente de validation de structure"]


class WaitingForAdageValidation(CheckBoxAnnotation):
    label: Literal["En attente de validation ADAGE"]


class MarkWithoutContinuationApplicationDetail(BaseModel):
    id: str
    number: int
    state: dms_models.GraphQLApplicationStates
    updated_at: datetime
    processing_error_pc: ProcessingErrorPassCulture | None
    waiting_for_offerer_validation: WaitingForOffererValidation | None
    waiting_for_adage_validation: WaitingForAdageValidation | None

    @validator("updated_at", pre=False)
    def strip_timezone(cls, value: datetime) -> datetime:
        return without_timezone(value)

    @root_validator(pre=True)
    def to_representation(cls: "MarkWithoutContinuationApplicationDetail", obj: dict) -> dict:
        to_representation = {}
        to_representation["id"] = obj["id"]
        to_representation["number"] = obj["number"]
        to_representation["state"] = obj["state"]
        to_representation["updated_at"] = obj["dateDerniereModification"]

        for annotation in obj["annotations"]:
            match annotation["label"]:
                case "Erreur traitement pass Culture":
                    to_representation["processing_error_pc"] = ProcessingErrorPassCulture(**annotation)
                case "En attente de validation de structure":
                    to_representation["waiting_for_offerer_validation"] = WaitingForOffererValidation(**annotation)
                case "En attente de validation ADAGE":
                    to_representation["waiting_for_adage_validation"] = WaitingForAdageValidation(**annotation)

        return to_representation

    @property
    def is_draft(self) -> bool:
        return self.state == dms_models.GraphQLApplicationStates.draft

    @property
    def should_be_marked_without_continuation(self) -> bool:
        dead_line_application = datetime.utcnow() - timedelta(
            days=int(settings.DS_MARK_WITHOUT_CONTINUATION_APPLICATION_DEADLINE)
        )
        dead_line_annotation = datetime.utcnow() - timedelta(
            days=int(settings.DS_MARK_WITHOUT_CONTINUATION_ANNOTATION_DEADLINE)
        )

        if self.updated_at < dead_line_application and self.state in (
            dms_models.GraphQLApplicationStates.draft,
            dms_models.GraphQLApplicationStates.on_going,
        ):
            if self.processing_error_pc is not None:
                logger.info(
                    "[DS] application is older than the dead line application", extra={"application_id": self.number}
                )
                if (
                    "adage" not in self.processing_error_pc.string_value
                    and "rct" not in self.processing_error_pc.string_value
                ):
                    logger.info("[DS] application is not about adage nor rct", extra={"application_id": self.number})
                    return True
                if (
                    "rct" in self.processing_error_pc.string_value
                    and self.processing_error_pc.updated_at < dead_line_annotation
                ):
                    logger.info(
                        "[DS] application is about `rct` but older than the dead line annotation",
                        extra={"application_id": self.number},
                    )
                    return True
            elif self.waiting_for_offerer_validation is not None and self.waiting_for_adage_validation is not None:
                if (
                    self.waiting_for_offerer_validation.checked is True
                    and self.waiting_for_offerer_validation.updated_at < dead_line_annotation
                ) and self.waiting_for_adage_validation.checked is False:
                    logger.info(
                        "[DS] application is waiting for offerer validation for too long",
                        extra={"application_id": self.number},
                    )
                    return True
                if (
                    self.waiting_for_offerer_validation.checked is False
                    and self.waiting_for_adage_validation.checked is False
                ):
                    logger.info(
                        "[DS] application is not waiting for validation of any kind",
                        extra={"application_id": self.number},
                    )
                    return True

        return False

    def mark_without_continuation(self) -> None:
        """Mark without continuation our internal representation of the DS application (BankAccount)"""
        mark_bank_account_without_continuation(self.number)
