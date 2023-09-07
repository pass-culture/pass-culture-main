import datetime
import enum

import pydantic.v1 as pydantic_v1


class UbbleIdentificationStatus(enum.Enum):
    UNINITIATED = "uninitiated"  # Identification has only been created (user has not started the verification flow)
    INITIATED = "initiated"  # User has started the verification flow
    PROCESSING = "processing"  # User has ended the verification flow, identification-url is not usable anymore
    PROCESSED = "processed"  # Identification is completely processed by Ubble
    ABORTED = "aborted"  # User has left the identification, the identification-url is no longer usable (this status is in beta test)
    EXPIRED = "expired"  # The identification-url has expired and is no longer usable (only uninitiated and initiated identifications can become expired)


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
