import datetime
import enum
import typing

import pydantic


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


class UbbleContent(pydantic.BaseModel):
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
    expiry_date_score: float = pydantic.Field(None, alias="expiry-date-score")
    supported: float


class UbbleIdentificationIncluded(pydantic.BaseModel):
    type: str
    id: int
    attributes: typing.Union[UbbleIdentificationDocumentChecks, UbbleIdentificationDocuments]
    relationships: typing.Optional[dict]


class UbbleIdentificationResponse(pydantic.BaseModel):
    data: UbbleIdentificationData
    included: list[UbbleIdentificationIncluded]
