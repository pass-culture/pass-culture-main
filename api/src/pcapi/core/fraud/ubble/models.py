import datetime
import enum

import pydantic
import pytz

from pcapi.core.users import models as users_models

from ..common.models import IdentityCheckContent


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


def _parse_ubble_gender(ubble_gender: str | None) -> users_models.GenderEnum | None:
    if ubble_gender == "M":
        return users_models.GenderEnum.M
    if ubble_gender == "F":
        return users_models.GenderEnum.F
    return None


class UbbleContent(IdentityCheckContent):
    birth_date: datetime.date | None
    comment: str | None
    document_type: str | None
    expiry_date_score: float | None
    first_name: str | None
    gender: users_models.GenderEnum | None
    id_document_number: str | None
    identification_id: pydantic.UUID4 | None
    identification_url: pydantic.HttpUrl | None
    last_name: str | None
    married_name: str | None
    ove_score: float | None
    reference_data_check_score: float | None
    registration_datetime: datetime.datetime | None
    processed_datetime: datetime.datetime | None
    score: float | None
    status: UbbleIdentificationStatus | None
    supported: float | None
    signed_image_front_url: pydantic.HttpUrl | None
    signed_image_back_url: pydantic.HttpUrl | None

    _parse_birth_date = pydantic.validator("birth_date", pre=True, allow_reuse=True)(
        lambda d: datetime.datetime.strptime(d, "%Y-%m-%d").date() if d is not None else None
    )
    _parse_gender = pydantic.validator("gender", pre=True, allow_reuse=True)(_parse_ubble_gender)

    def get_birth_date(self) -> datetime.date | None:
        return self.birth_date

    def get_registration_datetime(self) -> datetime.datetime | None:
        return (
            self.registration_datetime.astimezone(pytz.utc).replace(tzinfo=None) if self.registration_datetime else None
        )

    def get_first_name(self) -> str | None:
        return self.first_name

    def get_last_name(self) -> str | None:
        return self.last_name

    def get_civility(self) -> str | None:
        return self.gender.value if self.gender else None

    def get_married_name(self) -> str | None:
        return self.married_name

    def get_id_piece_number(self) -> str | None:
        return self.id_document_number


class UbbleIdentificationObject(pydantic.BaseModel):
    # Parent class for any object defined in https://ubbleai.github.io/developer-documentation/#objects-2
    pass


class UbbleIdentificationAttributes(UbbleIdentificationObject):
    # https://ubbleai.github.io/developer-documentation/#identifications
    comment: str | None
    created_at: datetime.datetime = pydantic.Field(alias="created-at")
    ended_at: datetime.datetime | None = pydantic.Field(None, alias="ended-at")
    identification_id: str = pydantic.Field(alias="identification-id")
    identification_url: str = pydantic.Field(alias="identification-url")
    number_of_attempts: int = pydantic.Field(alias="number-of-attempts")
    redirect_url: str = pydantic.Field(alias="redirect-url")
    score: float | None
    started_at: datetime.datetime | None = pydantic.Field(None, alias="started-at")
    status: UbbleIdentificationStatus
    status_updated_at: datetime.datetime = pydantic.Field(alias="status-updated-at")
    updated_at: datetime.datetime = pydantic.Field(alias="updated-at")
    user_agent: str | None = pydantic.Field(None, alias="user-agent")
    user_ip_address: str | None = pydantic.Field(None, alias="user-ip-address")
    webhook: str


class UbbleIdentificationData(pydantic.BaseModel):
    type: str
    id: int
    attributes: UbbleIdentificationAttributes


class UbbleIdentificationDocuments(UbbleIdentificationObject):
    # https://ubbleai.github.io/developer-documentation/#documents
    birth_date: str = pydantic.Field(None, alias="birth-date")
    document_number: str = pydantic.Field(None, alias="document-number")
    document_type: str = pydantic.Field(None, alias="document-type")
    first_name: str = pydantic.Field(None, alias="first-name")
    gender: str = pydantic.Field(None)
    last_name: str = pydantic.Field(None, alias="last-name")
    married_name: str = pydantic.Field(None, alias="married-name")
    signed_image_front_url: str = pydantic.Field(None, alias="signed-image-front-url")
    signed_image_back_url: str = pydantic.Field(None, alias="signed-image-back-url")


class UbbleIdentificationDocumentChecks(UbbleIdentificationObject):
    # https://ubbleai.github.io/developer-documentation/#document-checks
    data_extracted_score: float | None = pydantic.Field(None, alias="data-extracted-score")
    expiry_date_score: float | None = pydantic.Field(None, alias="expiry-date-score")
    issue_date_score: float | None = pydantic.Field(None, alias="issue-date-score")
    live_video_capture_score: float | None = pydantic.Field(None, alias="live-video-capture-score")
    mrz_validity_score: float | None = pydantic.Field(None, alias="mrz-validity-score")
    mrz_viz_score: float | None = pydantic.Field(None, alias="mrz-viz-score")
    ove_back_score: float | None = pydantic.Field(None, alias="ove-back-score")
    ove_front_score: float | None = pydantic.Field(None, alias="ove-front-score")
    ove_score: float | None = pydantic.Field(None, alias="ove-score")
    quality_score: float | None = pydantic.Field(None, alias="quality-score")
    score: float | None = pydantic.Field(None, alias="score")
    supported: float | None = None
    visual_back_score: float | None = pydantic.Field(None, alias="visual-back-score")
    visual_front_score: float | None = pydantic.Field(None, alias="visual-front-score")


class UbbleIdentificationFaceChecks(UbbleIdentificationObject):
    # https://ubbleai.github.io/developer-documentation/#face-checks
    active_liveness_score: float | None = pydantic.Field(None, alias="active-liveness-score")
    live_video_capture_score: float | None = pydantic.Field(None, alias="live-video-capture-score")
    quality_score: float | None = pydantic.Field(None, alias="quality-score")
    score: float | None = None


class UbbleIdentificationReferenceDataChecks(UbbleIdentificationObject):
    # https://ubbleai.github.io/developer-documentation/#reference-data-check
    score: float | None = None


class UbbleIdentificationDocFaceMatches(UbbleIdentificationObject):
    # https://ubbleai.github.io/developer-documentation/#doc-face-matches
    score: float | None = None


class UbbleIdentificationIncluded(pydantic.BaseModel):
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


class UbbleIdentificationResponse(pydantic.BaseModel):
    data: UbbleIdentificationData
    included: list[UbbleIdentificationIncluded]
