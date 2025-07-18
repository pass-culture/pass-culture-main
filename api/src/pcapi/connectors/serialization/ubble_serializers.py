import contextlib
import datetime
import enum
import logging
import re

import pydantic.v1 as pydantic_v1

from pcapi.core.fraud import models as fraud_models
from pcapi.core.users import models as users_models


logger = logging.getLogger(__name__)


class UbbleIdentificationStatus(enum.Enum):
    # ubble v2
    PENDING = "pending"
    CAPTURE_IN_PROGRESS = "capture_in_progress"
    CHECKS_IN_PROGRESS = "checks_in_progress"
    APPROVED = "approved"
    DECLINED = "declined"
    RETRY_REQUIRED = "retry_required"
    INCONCLUSIVE = "inconclusive"  # id verification is anonymized
    REFUSED = "refused"  # user did not consent to the verification
    # ubble v1
    UNINITIATED = "uninitiated"  # Identification has only been created (user has not started the verification flow)
    INITIATED = "initiated"  # User has started the verification flow
    PROCESSING = "processing"  # User has ended the verification flow, identification-url is not usable anymore
    PROCESSED = "processed"  # Identification is completely processed by Ubble
    ABORTED = "aborted"  # User has left the identification, the identification-url is no longer usable (this status is in beta test)
    EXPIRED = "expired"  # The identification-url has expired and is no longer usable (only uninitiated and initiated identifications can become expired)


class UbbleDeclaredData(pydantic_v1.BaseModel):
    name: str
    birth_date: datetime.date | None


class UbbleLink(pydantic_v1.BaseModel):
    href: pydantic_v1.HttpUrl


class UbbleLinks(pydantic_v1.BaseModel):
    self: UbbleLink
    verification_url: UbbleLink


class UbbleDocument(pydantic_v1.BaseModel):
    first_names: str | None
    full_name: str
    last_name: str | None
    birth_date: datetime.date | None
    birth_place: str | None
    document_type: str | None
    document_number: str | None
    gender: users_models.GenderEnum | None
    front_image_signed_url: str | None
    back_image_signed_url: str | None

    @pydantic_v1.validator("gender", pre=True)
    def parse_gender(cls, gender: str | None) -> users_models.GenderEnum | None:
        if not gender:
            return None
        with contextlib.suppress(KeyError):
            return users_models.GenderEnum[gender]
        return None


class UbbleResponseCode(pydantic_v1.BaseModel):
    code: int


class UbbleV2IdentificationResponse(pydantic_v1.BaseModel):
    # https://docs.ubble.ai/#tag/Identity-verifications/operation/create_and_start_identity_verification
    id: str
    applicant_id: str
    external_applicant_id: str | None
    user_journey_id: str
    status: UbbleIdentificationStatus
    links: UbbleLinks = pydantic_v1.Field(alias="_links")
    documents: list[UbbleDocument]
    response_codes: list[UbbleResponseCode]
    webhook_url: str
    redirect_url: str
    created_on: datetime.datetime
    modified_on: datetime.datetime

    @property
    def document(self) -> UbbleDocument | None:
        return self.documents[0] if self.documents else None

    @property
    def fraud_reason_codes(self) -> list["fraud_models.FraudReasonCode"]:
        return [
            fraud_models.UBBLE_REASON_CODE_MAPPING.get(
                response_code.code, fraud_models.FraudReasonCode.ID_CHECK_BLOCKED_OTHER
            )
            for response_code in self.response_codes
            if response_code.code != fraud_models.UBBLE_OK_REASON_CODE
        ]

    class Config:
        use_enum_values = True


def convert_identification_to_ubble_content(
    identification: UbbleV2IdentificationResponse,
) -> "fraud_models.UbbleContent":
    document = identification.document
    if not document:
        first_name, last_name = None, None
    else:
        first_name, last_name = _get_first_and_last_name(document)

    content = fraud_models.UbbleContent(
        applicant_id=identification.applicant_id,
        birth_date=getattr(document, "birth_date", None),
        birth_place=getattr(document, "birth_place", None),
        document_type=getattr(document, "document_type", None),
        external_applicant_id=identification.external_applicant_id,
        first_name=first_name,
        gender=getattr(document, "gender", None),
        id_document_number=getattr(document, "document_number", None),
        identification_id=identification.id,
        identification_url=identification.links.verification_url.href,
        last_name=last_name,
        reason_codes=identification.fraud_reason_codes,
        registration_datetime=identification.created_on,
        signed_image_back_url=getattr(document, "back_image_signed_url", None),
        signed_image_front_url=getattr(document, "front_image_signed_url", None),
        status=identification.status,
    )
    return content


def _get_first_and_last_name(document: UbbleDocument) -> tuple[str | None, str | None]:
    if document.first_names and document.last_name:
        return document.first_names.split(", ")[0], document.last_name

    if not document.full_name:
        return None, None

    logger.warning(
        "Name not composed of first names and last name: %s, defaulting to naive first name detection",
        document.full_name,
    )
    names = document.full_name.split(" ", maxsplit=1)
    if len(names) == 2:
        first_name, last_name = names
    else:
        first_name, last_name = "", names[0]
    return first_name, last_name


class UbbleV2ApplicantResponse(pydantic_v1.BaseModel):
    # https://docs.ubble.ai/#tag/Identity-verifications/operation/create_identity_verification
    id: str
    external_applicant_id: str | None


class UbbleV2AttemptResponse(pydantic_v1.BaseModel):
    # https://docs.ubble.ai/#tag/Identity-verifications/operation/create_attempt
    id: str
    links: UbbleLinks = pydantic_v1.Field(alias="_links")


class WebhookBodyData(pydantic_v1.BaseModel):
    # https://docs.ubble.ai/#section/Webhooks/Body
    identity_verification_id: str
    status: UbbleIdentificationStatus


class WebhookBodyV2(pydantic_v1.BaseModel):
    data: WebhookBodyData

    class Config:
        use_enum_values = True


# Ubble only consider HTTP status 200 and 201 as success
# but we are not able to respond with empty body unless we return a 204 HTTP status
# so we need a dummy reponse_model to be used for the webhook response
class WebhookDummyReponse(pydantic_v1.BaseModel):
    status: str = "ok"


class WebhookStoreIdPicturesRequest(pydantic_v1.BaseModel):
    identification_id: str


# DEPRECATED Ubble V1


class UbbleScore(enum.Enum):
    VALID = 1.0
    INVALID = 0.0
    UNDECIDABLE = -1.0


class UbbleIdentificationObject(pydantic_v1.BaseModel):
    # Parent class for any object defined in https://ubbleai.github.io/developer-documentation/#objects-2
    pass


class UbbleIdentificationAttributes(UbbleIdentificationObject):
    # https://ubbleai.github.io/developer-documentation/#identifications
    comment: str | None
    created_at: datetime.datetime = pydantic_v1.Field(alias="created-at")
    ended_at: datetime.datetime | None = pydantic_v1.Field(None, alias="ended-at")
    identification_id: str = pydantic_v1.Field(alias="identification-id")
    identification_url: str = pydantic_v1.Field(alias="identification-url")
    number_of_attempts: int = pydantic_v1.Field(alias="number-of-attempts")
    redirect_url: str = pydantic_v1.Field(alias="redirect-url")
    score: float | None
    started_at: datetime.datetime | None = pydantic_v1.Field(None, alias="started-at")
    status: UbbleIdentificationStatus
    status_updated_at: datetime.datetime = pydantic_v1.Field(alias="status-updated-at")
    updated_at: datetime.datetime = pydantic_v1.Field(alias="updated-at")
    user_agent: str | None = pydantic_v1.Field(None, alias="user-agent")
    user_ip_address: str | None = pydantic_v1.Field(None, alias="user-ip-address")
    webhook: str


class UbbleReasonCode(UbbleIdentificationObject):
    type: str = pydantic_v1.Field(alias="type")
    id: int = pydantic_v1.Field(alias="id")


class UbbleReasonCodes(UbbleIdentificationObject):
    data: list[UbbleReasonCode]


class UbbleIdentificationRelationships(UbbleIdentificationObject):
    reason_codes: UbbleReasonCodes = pydantic_v1.Field(alias="reason-codes")


class UbbleIdentificationData(pydantic_v1.BaseModel):
    type: str
    id: int
    attributes: UbbleIdentificationAttributes
    relationships: UbbleIdentificationRelationships


class UbbleIdentificationDocuments(UbbleIdentificationObject):
    # https://ubbleai.github.io/developer-documentation/#documents
    birth_date: str | None = pydantic_v1.Field(None, alias="birth-date")
    document_number: str | None = pydantic_v1.Field(None, alias="document-number")
    document_type: str | None = pydantic_v1.Field(None, alias="document-type")
    first_name: str | None = pydantic_v1.Field(None, alias="first-name")
    gender: str | None = pydantic_v1.Field(None)
    last_name: str | None = pydantic_v1.Field(None, alias="last-name")
    married_name: str | None = pydantic_v1.Field(None, alias="married-name")
    signed_image_front_url: str | None = pydantic_v1.Field(None, alias="signed-image-front-url")
    signed_image_back_url: str | None = pydantic_v1.Field(None, alias="signed-image-back-url")


class UbbleIdentificationDocumentChecks(UbbleIdentificationObject):
    # https://ubbleai.github.io/developer-documentation/#document-checks
    data_extracted_score: float | None = pydantic_v1.Field(None, alias="data-extracted-score")
    expiry_date_score: float | None = pydantic_v1.Field(None, alias="expiry-date-score")
    issue_date_score: float | None = pydantic_v1.Field(None, alias="issue-date-score")
    live_video_capture_score: float | None = pydantic_v1.Field(None, alias="live-video-capture-score")
    mrz_validity_score: float | None = pydantic_v1.Field(None, alias="mrz-validity-score")
    mrz_viz_score: float | None = pydantic_v1.Field(None, alias="mrz-viz-score")
    ove_back_score: float | None = pydantic_v1.Field(None, alias="ove-back-score")
    ove_front_score: float | None = pydantic_v1.Field(None, alias="ove-front-score")
    ove_score: float | None = pydantic_v1.Field(None, alias="ove-score")
    quality_score: float | None = pydantic_v1.Field(None, alias="quality-score")
    score: float | None = pydantic_v1.Field(None, alias="score")
    supported: float | None = None
    visual_back_score: float | None = pydantic_v1.Field(None, alias="visual-back-score")
    visual_front_score: float | None = pydantic_v1.Field(None, alias="visual-front-score")


class UbbleIdentificationFaceChecks(UbbleIdentificationObject):
    # https://ubbleai.github.io/developer-documentation/#face-checks
    active_liveness_score: float | None = pydantic_v1.Field(None, alias="active-liveness-score")
    live_video_capture_score: float | None = pydantic_v1.Field(None, alias="live-video-capture-score")
    quality_score: float | None = pydantic_v1.Field(None, alias="quality-score")
    score: float | None = None


class UbbleIdentificationReferenceDataChecks(UbbleIdentificationObject):
    # https://ubbleai.github.io/developer-documentation/#reference-data-check
    score: float | None = None


class UbbleIdentificationDocFaceMatches(UbbleIdentificationObject):
    # https://ubbleai.github.io/developer-documentation/#doc-face-matches
    score: float | None = None


class UbbleIdentificationIncluded(pydantic_v1.BaseModel):
    type: str
    id: int
    attributes: UbbleIdentificationObject
    relationships: dict | None


class UbbleIdentificationIncludedDocuments(UbbleIdentificationIncluded):
    attributes: UbbleIdentificationDocuments


class UbbleIdentificationIncludedDocumentChecks(UbbleIdentificationIncluded):
    attributes: UbbleIdentificationDocumentChecks


class UbbleIdentificationIncludedFaceChecks(UbbleIdentificationIncluded):
    attributes: UbbleIdentificationFaceChecks


class UbbleIdentificationIncludedReferenceDataChecks(UbbleIdentificationIncluded):
    attributes: UbbleIdentificationReferenceDataChecks


class UbbleIdentificationIncludedDocFaceMatches(UbbleIdentificationIncluded):
    attributes: UbbleIdentificationDocFaceMatches


class UbbleIdentificationResponse(pydantic_v1.BaseModel):
    data: UbbleIdentificationData
    included: list[UbbleIdentificationIncluded]


class Configuration(pydantic_v1.BaseModel):
    id: int
    name: str


class WebhookRequest(pydantic_v1.BaseModel):
    identification_id: str
    status: UbbleIdentificationStatus
    configuration: Configuration


UBBLE_SIGNATURE_RE = re.compile(r"^ts=(?P<ts>\d+),v1=(?P<v1>\S{64})$")


class WebhookRequestHeaders(pydantic_v1.BaseModel):
    ubble_signature: str = pydantic_v1.Field(..., regex=UBBLE_SIGNATURE_RE.pattern, alias="Ubble-Signature")

    class Config:
        extra = "allow"
