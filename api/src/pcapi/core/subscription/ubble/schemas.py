import datetime
import enum

import pydantic.v1 as pydantic_v1
import pytz
from pydantic import BaseModel as BaseModelV2

from pcapi.core.subscription import models as subscription_models
from pcapi.core.subscription import schemas as subscription_schemas
from pcapi.core.users import models as users_models


UBBLE_OK_REASON_CODE = 10000


UBBLE_REASON_CODE_MAPPING = {
    # Ubble V2 https://docs.ubble.ai/#section/Handle-verification-results/Response-codes
    61201: subscription_models.FraudReasonCode.NETWORK_CONNECTION_ISSUE,  # applicant did not have a sufficient connection
    61301: subscription_models.FraudReasonCode.BLURRY_DOCUMENT_VIDEO,  # applicant's document video is too blurry
    61302: subscription_models.FraudReasonCode.LACK_OF_LUMINOSITY,  # applicant performed their id verification under poor lighting conditions
    61312: subscription_models.FraudReasonCode.LACK_OF_LUMINOSITY,  # applicant hides part of the document
    61313: subscription_models.FraudReasonCode.LACK_OF_LUMINOSITY,  # applicant did not present a dynamic view of the document
    61901: subscription_models.FraudReasonCode.UBBLE_INTERNAL_ERROR,  # ubble messed up
    62101: subscription_models.FraudReasonCode.ID_CHECK_EXPIRED,  # applicant presented an expired document
    62102: subscription_models.FraudReasonCode.ID_CHECK_NOT_SUPPORTED,  # applicant presented a document which is not accepted
    62103: subscription_models.FraudReasonCode.DOCUMENT_DAMAGED,  # applicant has submitted a damaged document
    62201: subscription_models.FraudReasonCode.ID_CHECK_NOT_AUTHENTIC,  # applicant presented a photocopy of the document
    62202: subscription_models.FraudReasonCode.ID_CHECK_NOT_AUTHENTIC,  # applicant presented the document on a screen
    62301: subscription_models.FraudReasonCode.ID_CHECK_NOT_AUTHENTIC,  # applicant has submitted a counterfeit or falsification
    62304: subscription_models.FraudReasonCode.NOT_DOCUMENT_OWNER,  # applicant does not match the photograph of the document
    62401: subscription_models.FraudReasonCode.ID_CHECK_DATA_MATCH,  # applicant's identity does not match with the expected one
    # Ubble V1 https://ubbleai.github.io/developer-documentation/#reason-codes
    1201: subscription_models.FraudReasonCode.NETWORK_CONNECTION_ISSUE,  # applicant did not have a sufficient connection
    1301: subscription_models.FraudReasonCode.BLURRY_DOCUMENT_VIDEO,  # applicant's document video is too blurry
    1304: subscription_models.FraudReasonCode.LACK_OF_LUMINOSITY,  # applicant hides part of the document
    1305: subscription_models.FraudReasonCode.LACK_OF_LUMINOSITY,  # applicant did not present a dynamic view of the document
    1320: subscription_models.FraudReasonCode.LACK_OF_LUMINOSITY,  # applicant performed their id verification under poor lighting conditions
    1901: subscription_models.FraudReasonCode.UBBLE_INTERNAL_ERROR,  # ubble had trouble decoding the video
    2101: subscription_models.FraudReasonCode.ID_CHECK_EXPIRED,  # applicant presented an expired document
    2102: subscription_models.FraudReasonCode.ID_CHECK_NOT_SUPPORTED,  # applicant presented a document which is not accepted
    2103: subscription_models.FraudReasonCode.DOCUMENT_DAMAGED,  # applicant has submitted a damaged document
    2201: subscription_models.FraudReasonCode.ID_CHECK_NOT_AUTHENTIC,  # applicant presented a photocopy of the document
    2202: subscription_models.FraudReasonCode.ID_CHECK_NOT_AUTHENTIC,  # applicant presented the document on a screen
    2301: subscription_models.FraudReasonCode.ID_CHECK_NOT_AUTHENTIC,  # applicant has submitted a counterfeit or falsification
    2304: subscription_models.FraudReasonCode.NOT_DOCUMENT_OWNER,  # applicant is not the rightful owner of the document
    2401: subscription_models.FraudReasonCode.ID_CHECK_DATA_MATCH,  # applicant's identity does not match with the expected one
}


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


class UbbleContent(subscription_schemas.IdentityCheckContent):
    applicant_id: str | None = None
    birth_date: datetime.date | None = None
    birth_place: str | None = None
    comment: str | None = None
    document_type: str | None = None
    expiry_date_score: float | None = None
    external_applicant_id: str | None = None
    first_name: str | None = None
    gender: users_models.GenderEnum | None = None
    id_document_number: str | None = None
    identification_id: str | None = None
    identification_url: pydantic_v1.HttpUrl | None = None
    last_name: str | None = None
    married_name: str | None = None
    ove_score: float | None = None
    processed_datetime: datetime.datetime | None = None
    reason_codes: list[subscription_models.FraudReasonCode] | None = None
    reference_data_check_score: float | None = None
    registration_datetime: datetime.datetime | None = None
    score: float | None = None
    signed_image_back_url: pydantic_v1.HttpUrl | None = None
    signed_image_front_url: pydantic_v1.HttpUrl | None = None
    status: UbbleIdentificationStatus | None = None
    status_updated_at: datetime.datetime | None = None
    supported: float | None = None

    @pydantic_v1.validator("birth_date", pre=True)
    def parse_birth_date(cls, birth_date: datetime.date | str | None) -> datetime.date | None:
        if isinstance(birth_date, datetime.date):
            return birth_date
        if isinstance(birth_date, str):
            return datetime.datetime.strptime(birth_date, "%Y-%m-%d").date()
        return None

    def get_birth_date(self) -> datetime.date | None:
        return self.birth_date

    def get_birth_place(self) -> str | None:
        return self.birth_place

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


class UpdateWorkflowPayload(BaseModelV2):
    beneficiary_fraud_check_id: int


class StoreIdPicturePayload(BaseModelV2):
    identification_id: str
