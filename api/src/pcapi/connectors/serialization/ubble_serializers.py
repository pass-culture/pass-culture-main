import contextlib
import datetime
import enum
import logging
import re

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field
from pydantic import HttpUrl
from pydantic import SerializeAsAny
from pydantic import field_validator

from pcapi.core.subscription import models as subscription_models
from pcapi.core.subscription.ubble import schemas as ubble_schemas
from pcapi.core.users import models as users_models
from pcapi.routes.serialization import HttpBodyModel


logger = logging.getLogger(__name__)


class UbbleDeclaredData(BaseModel):
    name: str
    birth_date: datetime.date | None = None


class UbbleLink(BaseModel):
    href: HttpUrl


class UbbleLinks(BaseModel):
    self: UbbleLink
    verification_url: UbbleLink


class UbbleDocument(BaseModel):
    first_names: str | None = None
    full_name: str
    last_name: str | None = None
    last_name_at_birth: str | None = None
    birth_date: datetime.date | None = None
    birth_place: str | None = None
    nationality: str | None = None
    document_type: str | None = None
    document_issuing_country: str | None = None
    document_number: str | None = None
    gender: users_models.GenderEnum | None = None
    front_image_signed_url: str | None = None
    back_image_signed_url: str | None = None

    @field_validator("gender", mode="before")
    def parse_gender(cls, gender: str | None) -> users_models.GenderEnum | None:
        if not gender:
            return None
        with contextlib.suppress(KeyError):
            return users_models.GenderEnum[gender]
        return None


class UbbleResponseCode(BaseModel):
    code: int


class UbbleV2IdentificationResponse(BaseModel):
    # https://docs.ubble.ai/#tag/Identity-verifications/operation/create_and_start_identity_verification
    id: str
    applicant_id: str
    external_applicant_id: str | None = None
    user_journey_id: str
    status: ubble_schemas.UbbleIdentificationStatus
    links: UbbleLinks = Field(alias="_links")
    documents: list[UbbleDocument]
    response_codes: list[UbbleResponseCode]
    webhook_url: str
    redirect_url: str
    created_on: datetime.datetime
    modified_on: datetime.datetime

    model_config = ConfigDict(use_enum_values=True)

    @property
    def document(self) -> UbbleDocument | None:
        return self.documents[0] if self.documents else None

    @property
    def fraud_reason_codes(self) -> list["subscription_models.FraudReasonCode"]:
        return [
            ubble_schemas.UBBLE_REASON_CODE_MAPPING.get(
                response_code.code, subscription_models.FraudReasonCode.ID_CHECK_BLOCKED_OTHER
            )
            for response_code in self.response_codes
            if response_code.code != ubble_schemas.UBBLE_OK_REASON_CODE
        ]


def convert_identification_to_ubble_content(
    identification: UbbleV2IdentificationResponse,
) -> "ubble_schemas.UbbleContent":
    document = identification.document
    if not document:
        first_name, last_name, last_name_at_birth = None, None, None
    else:
        first_name, last_name = _get_first_and_last_name(document)
        last_name_at_birth = document.last_name_at_birth

    content = ubble_schemas.UbbleContent(
        applicant_id=identification.applicant_id,
        birth_date=getattr(document, "birth_date", None),
        birth_place=getattr(document, "birth_place", None),
        document_issuing_country=getattr(document, "document_issuing_country", None),
        document_type=getattr(document, "document_type", None),
        external_applicant_id=identification.external_applicant_id,
        first_name=first_name,
        gender=getattr(document, "gender", None),
        id_document_number=getattr(document, "document_number", None),
        identification_id=identification.id,
        identification_url=identification.links.verification_url.href,
        last_name=last_name,
        last_name_at_birth=last_name_at_birth,
        nationality=getattr(document, "nationality", None),
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


class UbbleV2ApplicantResponse(BaseModel):
    # https://docs.ubble.ai/#tag/Identity-verifications/operation/create_identity_verification
    id: str
    external_applicant_id: str | None = None


class UbbleV2AttemptResponse(BaseModel):
    # https://docs.ubble.ai/#tag/Identity-verifications/operation/create_attempt
    id: str
    links: UbbleLinks = Field(alias="_links")


class AttemptStatus(enum.StrEnum):
    PENDING_REDIRECTION = enum.auto()
    CAPTURE_IN_PROGRESS = enum.auto()
    CHECKS_IN_PROGRESS = enum.auto()
    COMPLETED = enum.auto()
    EXPIRED = enum.auto()
    CAPTURE_ABORTED = enum.auto()
    CAPTURE_REFUSED = enum.auto()
    CHECKS_INCONCLUSIVE = enum.auto()
    TERMINATED = enum.auto()


class AttemptData(BaseModel):
    id: str
    status: AttemptStatus


class GetAttemptsResponse(BaseModel):
    data: list[AttemptData]


class UbbleLinkV2(BaseModel):
    href: HttpUrl


class AssetType(enum.StrEnum):
    FACE_IMAGE = enum.auto()
    FACE_VIDEO = enum.auto()
    DOCUMENT_FRONT_IMAGE = enum.auto()
    DOCUMENT_BACK_IMAGE = enum.auto()
    DOCUMENT_FRONT_VIDEO = enum.auto()
    DOCUMENT_SIGNATURE_IMAGE = enum.auto()
    DOCUMENT_BACK_VIDEO = enum.auto()
    SECONDARY_DOCUMENT_FRONT_VIDEO = enum.auto()
    SECONDARY_DOCUMENT_FRONT_IMAGE = enum.auto()
    SECONDARY_DOCUMENT_BACK_IMAGE = enum.auto()
    SECONDARY_DOCUMENT_SIGNATURE_IMAGE = enum.auto()
    SECONDARY_DOCUMENT_BACK_VIDEO = enum.auto()


class AssetLink(BaseModel):
    asset_url: UbbleLinkV2


class AttemptAssetData(BaseModel):
    type: AssetType
    links: AssetLink = Field(validation_alias="_links")


class GetAttemptAssetsResponse(BaseModel):
    data: list[AttemptAssetData]


class WebhookBodyData(HttpBodyModel):
    # https://docs.ubble.ai/#section/Webhooks/Body
    identity_verification_id: str
    status: ubble_schemas.UbbleIdentificationStatus

    model_config = ConfigDict(extra="ignore")


class WebhookBodyV2(HttpBodyModel):
    data: WebhookBodyData

    model_config = ConfigDict(use_enum_values=True, extra="ignore")


# Ubble only consider HTTP status 200 and 201 as success
# but we are not able to respond with empty body unless we return a 204 HTTP status
# so we need a dummy reponse_model to be used for the webhook response
class WebhookDummyReponse(HttpBodyModel):
    status: str = "ok"


class WebhookStoreIdPicturesRequest(BaseModel):
    identification_id: str


# DEPRECATED Ubble V1


class UbbleScore(enum.Enum):
    VALID = 1.0
    INVALID = 0.0
    UNDECIDABLE = -1.0


class UbbleIdentificationObject(BaseModel):
    # Parent class for any object defined in https://ubbleai.github.io/developer-documentation/#objects-2
    pass


class UbbleIdentificationAttributes(UbbleIdentificationObject):
    # https://ubbleai.github.io/developer-documentation/#identifications
    comment: str | None = None
    created_at: datetime.datetime = Field(alias="created-at")
    ended_at: datetime.datetime | None = Field(None, alias="ended-at")
    identification_id: str = Field(alias="identification-id")
    identification_url: str = Field(alias="identification-url")
    number_of_attempts: int = Field(alias="number-of-attempts")
    redirect_url: str = Field(alias="redirect-url")
    score: float | None = None
    started_at: datetime.datetime | None = Field(None, alias="started-at")
    status: ubble_schemas.UbbleIdentificationStatus
    status_updated_at: datetime.datetime = Field(alias="status-updated-at")
    updated_at: datetime.datetime = Field(alias="updated-at")
    user_agent: str | None = Field(None, alias="user-agent")
    user_ip_address: str | None = Field(None, alias="user-ip-address")
    webhook: str


class UbbleReasonCode(UbbleIdentificationObject):
    type: str = Field(alias="type")
    id: int = Field(alias="id")


class UbbleReasonCodes(UbbleIdentificationObject):
    data: list[UbbleReasonCode]


class UbbleIdentificationRelationships(UbbleIdentificationObject):
    reason_codes: UbbleReasonCodes = Field(alias="reason-codes")


class UbbleIdentificationData(BaseModel):
    type: str
    id: int
    attributes: UbbleIdentificationAttributes
    relationships: UbbleIdentificationRelationships


class UbbleIdentificationDocuments(UbbleIdentificationObject):
    # https://ubbleai.github.io/developer-documentation/#documents
    birth_date: str | None = Field(None, alias="birth-date")
    document_number: str | None = Field(None, alias="document-number")
    document_type: str | None = Field(None, alias="document-type")
    first_name: str | None = Field(None, alias="first-name")
    gender: str | None = Field(None)
    last_name: str | None = Field(None, alias="last-name")
    married_name: str | None = Field(None, alias="married-name")
    signed_image_front_url: str | None = Field(None, alias="signed-image-front-url")
    signed_image_back_url: str | None = Field(None, alias="signed-image-back-url")


class UbbleIdentificationDocumentChecks(UbbleIdentificationObject):
    # https://ubbleai.github.io/developer-documentation/#document-checks
    data_extracted_score: float | None = Field(None, alias="data-extracted-score")
    expiry_date_score: float | None = Field(None, alias="expiry-date-score")
    issue_date_score: float | None = Field(None, alias="issue-date-score")
    live_video_capture_score: float | None = Field(None, alias="live-video-capture-score")
    mrz_validity_score: float | None = Field(None, alias="mrz-validity-score")
    mrz_viz_score: float | None = Field(None, alias="mrz-viz-score")
    ove_back_score: float | None = Field(None, alias="ove-back-score")
    ove_front_score: float | None = Field(None, alias="ove-front-score")
    ove_score: float | None = Field(None, alias="ove-score")
    quality_score: float | None = Field(None, alias="quality-score")
    score: float | None = Field(None, alias="score")
    supported: float | None = None
    visual_back_score: float | None = Field(None, alias="visual-back-score")
    visual_front_score: float | None = Field(None, alias="visual-front-score")


class UbbleIdentificationFaceChecks(UbbleIdentificationObject):
    # https://ubbleai.github.io/developer-documentation/#face-checks
    active_liveness_score: float | None = Field(None, alias="active-liveness-score")
    live_video_capture_score: float | None = Field(None, alias="live-video-capture-score")
    quality_score: float | None = Field(None, alias="quality-score")
    score: float | None = None


class UbbleIdentificationReferenceDataChecks(UbbleIdentificationObject):
    # https://ubbleai.github.io/developer-documentation/#reference-data-check
    score: float | None = None


class UbbleIdentificationDocFaceMatches(UbbleIdentificationObject):
    # https://ubbleai.github.io/developer-documentation/#doc-face-matches
    score: float | None = None


class UbbleIdentificationIncluded(BaseModel):
    type: str
    id: int
    attributes: UbbleIdentificationObject
    relationships: dict | None = None


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


class UbbleIdentificationResponse(BaseModel):
    data: UbbleIdentificationData
    included: list[SerializeAsAny[UbbleIdentificationIncluded]]


class Configuration(BaseModel):
    id: int
    name: str


class WebhookRequest(BaseModel):
    identification_id: str
    status: ubble_schemas.UbbleIdentificationStatus
    configuration: Configuration


UBBLE_SIGNATURE_RE = re.compile(r"^ts=(?P<ts>\d+),v1=(?P<v1>\S{64})$")


class WebhookRequestHeaders(BaseModel):
    ubble_signature: str = Field(pattern=UBBLE_SIGNATURE_RE.pattern, alias="Ubble-Signature")

    model_config = ConfigDict(extra="allow")
