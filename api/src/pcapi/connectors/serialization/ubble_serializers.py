import contextlib
import datetime

import pydantic.v1 as pydantic_v1

from pcapi.core.fraud import models as fraud_models
from pcapi.core.fraud.ubble import models as ubble_models
from pcapi.core.users import models as users_models


class UbbleDeclaredData(pydantic_v1.BaseModel):
    name: str
    birth_date: datetime.date | None


class UbbleLink(pydantic_v1.BaseModel):
    href: pydantic_v1.HttpUrl


class UbbleLinks(pydantic_v1.BaseModel):
    self: UbbleLink
    applicant: UbbleLink
    verification_url: UbbleLink


class UbbleDocument(pydantic_v1.BaseModel):
    full_name: str
    birth_date: datetime.date | None
    document_type: str
    document_number: str | None
    gender: users_models.GenderEnum | None
    front_image_signed_url: str
    back_image_signed_url: str | None

    @pydantic_v1.validator("gender", pre=True)
    def parse_gender(cls, gender: str | None) -> users_models.GenderEnum | None:
        if not gender:
            return None
        with contextlib.suppress(KeyError):
            return users_models.GenderEnum[gender]
        return None


class UbbleResponseCode(pydantic_v1.BaseModel):
    response_code: int


class UbbleIdentificationResponse(pydantic_v1.BaseModel):
    # https://docs.ubble.ai/#tag/Identity-verifications/operation/create_and_start_identity_verification
    id: str
    applicant_id: str
    user_journey_id: str
    # TODO clean up imports
    status: ubble_models.UbbleIdentificationStatus
    declared_data: UbbleDeclaredData
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
    def fraud_reason_codes(self) -> list[fraud_models.FraudReasonCode]:
        return [
            fraud_models.UBBLE_REASON_CODE_MAPPING.get(
                response_code.response_code, fraud_models.FraudReasonCode.ID_CHECK_BLOCKED_OTHER
            )
            for response_code in self.response_codes
        ]

    class Config:
        use_enum_values = True


def convert_identification_to_ubble_content(identification: UbbleIdentificationResponse) -> fraud_models.UbbleContent:
    document = identification.document
    if not document:
        first_name, last_name = None, None
    else:
        first_name, last_name = document.full_name.split(" ", maxsplit=1)

    content = fraud_models.UbbleContent(
        birth_date=getattr(document, "birth_date", None),
        document_type=getattr(document, "document_type", None),
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
        comment=None,
        expiry_date_score=None,
        married_name=None,
        ove_score=None,
        reference_data_check_score=None,
        processed_datetime=None,
        score=None,
        status_updated_at=None,
        supported=None,
    )
    return content
