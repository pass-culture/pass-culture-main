import datetime
import enum
import typing

import pydantic

from .common import IdentityCheckContent


class UbbleIdentificationStatus(enum.Enum):
    UNINITIATED = "uninitiated"
    INITIATED = "initiated"
    PROCESSING = "processing"
    PROCESSED = "processed"
    ABORTED = "aborted"


class UbbleScore(enum.Enum):
    VALID = 1.0
    INVALID = 0.0
    UNDECIDABLE = -1.0


class UbbleContent(IdentityCheckContent):
    birth_date: typing.Optional[datetime.date]
    comment: typing.Optional[str]
    document_type: typing.Optional[str]
    expiry_date_score: typing.Optional[float]
    first_name: typing.Optional[str]
    id_document_number: typing.Optional[str]
    identification_id: typing.Optional[pydantic.UUID4]
    identification_url: typing.Optional[pydantic.HttpUrl]
    last_name: typing.Optional[str]
    registration_datetime: typing.Optional[datetime.datetime]
    score: typing.Optional[float]
    status: typing.Optional[UbbleIdentificationStatus]
    supported: typing.Optional[float]

    _parse_birth_date = pydantic.validator("birth_date", pre=True, allow_reuse=True)(
        lambda d: datetime.datetime.strptime(d, "%Y-%m-%d").date() if d is not None else None
    )

    def get_registration_datetime(self) -> typing.Optional[datetime.datetime]:
        return self.registration_datetime

    def get_birth_date(self) -> typing.Optional[datetime.date]:
        return self.birth_date


class UbbleIdentificationAttributes(pydantic.BaseModel):
    comment: typing.Optional[str]
    created_at: datetime.datetime = pydantic.Field(alias="created-at")
    ended_at: typing.Optional[datetime.datetime] = pydantic.Field(None, alias="ended-at")
    identification_id: str = pydantic.Field(alias="identification-id")
    identification_url: str = pydantic.Field(alias="identification-url")
    number_of_attempts: int = pydantic.Field(alias="number-of-attempts")
    redirect_url: str = pydantic.Field(alias="redirect-url")
    score: typing.Optional[float]
    started_at: typing.Optional[datetime.datetime] = pydantic.Field(None, alias="started-at")
    status: UbbleIdentificationStatus
    status_updated_at: datetime.datetime = pydantic.Field(alias="status-updated-at")
    updated_at: datetime.datetime = pydantic.Field(alias="updated-at")
    user_agent: typing.Optional[str] = pydantic.Field(None, alias="user-agent")
    user_ip_address: typing.Optional[str] = pydantic.Field(None, alias="user-ip-address")
    webhook: str


class UbbleIdentificationData(pydantic.BaseModel):
    type: str
    id: int
    attributes: UbbleIdentificationAttributes


class UbbleIdentificationDocuments(pydantic.BaseModel):
    birth_date: str = pydantic.Field(None, alias="birth-date")
    document_number: str = pydantic.Field(None, alias="document-number")
    document_type: str = pydantic.Field(None, alias="document-type")
    first_name: str = pydantic.Field(None, alias="first-name")
    last_name: str = pydantic.Field(None, alias="last-name")


class UbbleIdentificationDocumentChecks(pydantic.BaseModel):
    data_extracted_score: typing.Optional[float] = pydantic.Field(None, alias="data-extracted-score")
    expiry_date_score: typing.Optional[float] = pydantic.Field(None, alias="expiry-date-score")
    issue_date_score: typing.Optional[float] = pydantic.Field(None, alias="issue-date-score")
    live_video_capture_score: typing.Optional[float] = pydantic.Field(None, alias="live-video-capture-score")
    mrz_validity_score: typing.Optional[float] = pydantic.Field(None, alias="mrz-validity-score")
    mrz_viz_score: typing.Optional[float] = pydantic.Field(None, alias="mrz-viz-score")
    ove_back_score: typing.Optional[float] = pydantic.Field(None, alias="ove-back-score")
    ove_front_score: typing.Optional[float] = pydantic.Field(None, alias="ove-front-score")
    ove_score: typing.Optional[float] = pydantic.Field(None, alias="ove-score")
    quality_score: typing.Optional[float] = pydantic.Field(None, alias="quality-score")
    score: typing.Optional[float] = pydantic.Field(None, alias="score")
    supported: typing.Optional[float] = None
    visual_back_score: typing.Optional[float] = pydantic.Field(None, alias="visual-back-score")
    visual_front_score: typing.Optional[float] = pydantic.Field(None, alias="visual-front-score")


class UbbleIdentificationFaceChecks(pydantic.BaseModel):
    active_liveness_score: typing.Optional[float] = pydantic.Field(None, alias="active-liveness-score")
    live_video_capture_score: typing.Optional[float] = pydantic.Field(None, alias="live-video-capture-score")
    quality_score: typing.Optional[float] = pydantic.Field(None, alias="quality-score")
    score: typing.Optional[float] = None


class UbbleIdentificationReferenceDataChecks(pydantic.BaseModel):
    score: typing.Optional[float] = None


class UbbleIdentificationDocFaceMatches(pydantic.BaseModel):
    score: typing.Optional[float] = None


class UbbleIdentificationIncluded(pydantic.BaseModel):
    type: str
    id: int
    attributes: typing.Union[UbbleIdentificationDocumentChecks, UbbleIdentificationDocuments]
    relationships: typing.Optional[dict]


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


class UbbleIdentificationResponse(pydantic.BaseModel):
    data: UbbleIdentificationData
    included: list[UbbleIdentificationIncluded]
