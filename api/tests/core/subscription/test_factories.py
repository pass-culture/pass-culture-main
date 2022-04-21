from collections import defaultdict
import datetime
from enum import Enum
import random
import string
import uuid

from dateutil.relativedelta import relativedelta
import factory
import pytz

from pcapi import settings
from pcapi.core.fraud.ubble import models as ubble_fraud_models


class IdentificationState(Enum):
    NEW = "new"
    INITIATED = "initiated"
    PROCESSING = "processing"
    VALID = "valid"
    INVALID = "invalid"
    UNPROCESSABLE = "unprocessable"
    ABORTED = "aborted"


STATE_STATUS_MAPPING = {
    IdentificationState.NEW: ubble_fraud_models.UbbleIdentificationStatus.UNINITIATED,
    IdentificationState.INITIATED: ubble_fraud_models.UbbleIdentificationStatus.INITIATED,
    IdentificationState.ABORTED: ubble_fraud_models.UbbleIdentificationStatus.ABORTED,
    IdentificationState.PROCESSING: ubble_fraud_models.UbbleIdentificationStatus.PROCESSING,
    IdentificationState.VALID: ubble_fraud_models.UbbleIdentificationStatus.PROCESSED,
    IdentificationState.INVALID: ubble_fraud_models.UbbleIdentificationStatus.PROCESSED,
    IdentificationState.UNPROCESSABLE: ubble_fraud_models.UbbleIdentificationStatus.PROCESSED,
}


class IdentificationIncludedType(Enum):
    DOCUMENT_CHECKS = "document-checks"
    DOCUMENTS = "documents"
    FACE_CHECKS = "face-checks"
    REFERENCE_DATA_CHECKS = "reference-data-checks"
    DOC_FACE_MATCHES = "doc-face-matches"


class UbbleIdentificationDataAttributesFactory(factory.Factory):
    class Meta:
        model = ubble_fraud_models.UbbleIdentificationAttributes
        rename = {
            "anonymized_at": "anonymized-at",
            "created_at": "created-at",
            "ended_at": "ended-at",
            "identification_id": "identification-id",
            "identification_url": "identification-url",
            "is_live": "is-live",
            "number_of_attempts": "number-of-attempts",
            "redirect_url": "redirect-url",
            "started_at": "started-at",
            "updated_at": "updated-at",
            "status_updated_at": "status-updated-at",
            "user_agent": "user-agent",
            "user_ip_address": "user-ip-address",
        }

    class Params:
        identification_state = IdentificationState.NEW

    anonymized_at = None
    # The use of `datetime.now()` here is legit, because the Ubble API
    # sends a formatted UTC datetime and pydantic turns it into a
    # timezone-aware datetime.
    created_at = factory.LazyFunction(lambda: datetime.datetime.now(tz=pytz.utc))  # pylint: disable=datetime-now
    identification_id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    identification_url = factory.LazyAttribute(
        lambda o: f"{settings.UBBLE_API_URL}/identifications/{o.identification_id}"
    )
    is_live = False
    redirect_url = "http://example.com"
    webhook = ""

    @factory.lazy_attribute
    def comment(self):
        return {
            IdentificationState.PROCESSING: "Some additional elements need to be verified.",
            IdentificationState.INVALID: "Extracted identity and reference data do not match.",
            IdentificationState.VALID: "",
        }.get(self.identification_state)

    @factory.lazy_attribute
    def number_of_attempts(self):
        return 0 if self.identification_state == IdentificationState.NEW else 1

    @factory.lazy_attribute
    def score(self):
        return {
            IdentificationState.UNPROCESSABLE: ubble_fraud_models.UbbleScore.UNDECIDABLE.value,
            IdentificationState.INVALID: ubble_fraud_models.UbbleScore.INVALID.value,
            IdentificationState.VALID: ubble_fraud_models.UbbleScore.VALID.value,
        }.get(self.identification_state)

    @factory.lazy_attribute
    def started_at(self):
        return None if self.identification_state == IdentificationState.NEW else datetime.datetime.utcnow()

    @factory.lazy_attribute
    def ended_at(self):
        return (
            datetime.datetime.utcnow()
            if self.identification_state
            in (IdentificationState.VALID, IdentificationState.INVALID, IdentificationState.UNPROCESSABLE)
            else None
        )

    @factory.lazy_attribute
    def status_updated_at(self):
        return {
            IdentificationState.NEW: self.created_at,
            IdentificationState.INITIATED: self.started_at,
            IdentificationState.ABORTED: datetime.datetime.utcnow(),
            IdentificationState.PROCESSING: datetime.datetime.utcnow(),
            IdentificationState.VALID: self.ended_at,
            IdentificationState.INVALID: self.ended_at,
            IdentificationState.UNPROCESSABLE: self.ended_at,
        }.get(self.identification_state)

    @factory.lazy_attribute
    def status(self):
        return STATE_STATUS_MAPPING.get(self.identification_state)

    @factory.lazy_attribute
    def updated_at(self):
        return {
            IdentificationState.NEW: self.created_at,
            IdentificationState.INITIATED: self.started_at,
            IdentificationState.ABORTED: datetime.datetime.utcnow(),
            IdentificationState.PROCESSING: datetime.datetime.utcnow(),
            IdentificationState.VALID: self.ended_at,
            IdentificationState.INVALID: self.ended_at,
            IdentificationState.UNPROCESSABLE: self.ended_at,
        }.get(self.identification_state)

    @factory.lazy_attribute
    def user_agent(self):
        return (
            factory.faker.faker.Faker().user_agent()
            if self.identification_state
            in (
                IdentificationState.PROCESSING,
                IdentificationState.VALID,
                IdentificationState.INVALID,
                IdentificationState.UNPROCESSABLE,
            )
            else None
        )

    @factory.lazy_attribute
    def user_ip_address(self):
        return (
            factory.faker.faker.Faker().ipv4()
            if self.identification_state
            in (
                IdentificationState.PROCESSING,
                IdentificationState.VALID,
                IdentificationState.INVALID,
                IdentificationState.UNPROCESSABLE,
            )
            else None
        )


class UbbleIdentificationDataFactory(factory.Factory):
    class Meta:
        model = ubble_fraud_models.UbbleIdentificationData

    class Params:
        identification_state = IdentificationState.NEW

    type = "identifications"
    id = factory.Faker("pyint")
    attributes = factory.SubFactory(
        UbbleIdentificationDataAttributesFactory,
        identification_state=factory.SelfAttribute("..identification_state"),
    )


class UbbleIdentificationIncludedDocumentsAttributesFactory(factory.Factory):
    class Meta:
        model = ubble_fraud_models.UbbleIdentificationDocuments
        rename = {
            "birth_date": "birth-date",
            "birth_place": "birth-place",
            "document_number": "document-number",
            "document_type": "document-type",
            "document_type_detailed": "document-type-detailed",
            "expiry_date": "expiry-date",
            "first_name": "first-name",
            "gender": "gender",
            "issue_date": "issue-date",
            "issue_place": "issue-place",
            "issuing_state_code": "issuing-state-code",
            "last_name": "last-name",
            "married_name": "married-name",
            "signed_image_front_url": "signed-image-front-url",
            "signed_image_back_url": "signed-image-back-url",
        }

    birth_date = factory.LazyFunction(lambda: str(datetime.date.today() - relativedelta(years=18)))
    birth_place = None
    document_number = factory.LazyFunction(lambda: "".join(random.choice(string.digits) for _ in range(12)))
    document_type = "ID"
    document_type_detailed = None
    expiry_date = None
    first_name = factory.Faker("first_name")
    gender = "M"
    issue_date = None
    issue_place = None
    issuing_state_code = None
    last_name = factory.Faker("last_name")
    married_name = factory.Faker("last_name")
    media_type = None
    mrz = None
    nationality = None
    obtaining_date = None
    personal_number = None
    remarks = None
    signed_image_front_url = None
    signed_image_back_url = None


class UbbleIdentificationIncludedDocumentChecksAttributesFactory(factory.Factory):
    class Meta:
        model = ubble_fraud_models.UbbleIdentificationDocumentChecks
        rename = {
            "data_extracted_score": "data-extracted-score",
            "expiry_date_score": "expiry-date-score",
            "issue_date_score": "issue-date-score",
            "live_video_capture_score": "live-video-capture-score",
            "mrz_validity_score": "mrz-validity-score",
            "mrz_viz_score": "mrz-viz-score",
            "ove_back_score": "ove-back-score",
            "ove_front_score": "ove-front-score",
            "ove_score": "ove-score",
            "quality_score": "quality-score",
            "visual_back_score": "visual-back-score",
            "visual_front_score": "visual-front-score",
        }

    class Params:
        identification_state = IdentificationState.VALID

    data_extracted_score = None
    expiry_date_score = ubble_fraud_models.UbbleScore.VALID.value
    issue_date_score = None
    live_video_capture_score = None
    mrz_validity_score = None
    mrz_viz_score = None
    ove_back_score = None
    ove_front_score = None
    ove_score = None
    quality_score: None
    supported = ubble_fraud_models.UbbleScore.VALID.value
    visual_back_score = None
    visual_front_score = None

    @factory.lazy_attribute
    def score(self):
        return {
            IdentificationState.UNPROCESSABLE: ubble_fraud_models.UbbleScore.INVALID.value,
            IdentificationState.INVALID: ubble_fraud_models.UbbleScore.INVALID.value,
            IdentificationState.VALID: ubble_fraud_models.UbbleScore.VALID.value,
        }.get(self.identification_state)


class UbbleIdentificationIncludedDocFaceMatchesAttributesFactory(factory.Factory):
    class Meta:
        model = ubble_fraud_models.UbbleIdentificationDocFaceMatches

    class Params:
        identification_state = IdentificationState.VALID

    score = ubble_fraud_models.UbbleScore.VALID.value


class UbbleIdentificationIncludedFaceChecksAttributesFactory(factory.Factory):
    class Meta:
        model = ubble_fraud_models.UbbleIdentificationFaceChecks
        rename = {
            "active_liveness_score": "active-liveness-score",
            "live_video_capture_score": "live-video-capture-score",
            "quality_score": "quality-score",
        }

    class Params:
        identification_state = IdentificationState.VALID

    active_liveness_score = None
    live_video_capture_score = None
    quality_score = None
    score = ubble_fraud_models.UbbleScore.VALID.value


class UbbleIdentificationIncludedReferenceDataChecksAttributesFactory(factory.Factory):
    class Meta:
        model = ubble_fraud_models.UbbleIdentificationReferenceDataChecks

    score = ubble_fraud_models.UbbleScore.VALID.value


class UbbleIdentificationIncludedFactory(factory.Factory):
    class Meta:
        model = ubble_fraud_models.UbbleIdentificationIncluded
        abstract = True

    type = None
    id = factory.Faker("pyint")
    attributes = None


class UbbleIdentificationIncludedDocumentsFactory(UbbleIdentificationIncludedFactory):
    class Meta:
        model = ubble_fraud_models.UbbleIdentificationIncludedDocuments

    type = IdentificationIncludedType.DOCUMENTS.value
    attributes = factory.SubFactory(UbbleIdentificationIncludedDocumentsAttributesFactory)


class UbbleIdentificationIncludedDocumentChecksFactory(UbbleIdentificationIncludedFactory):
    class Meta:
        model = ubble_fraud_models.UbbleIdentificationIncludedDocumentChecks

    type = IdentificationIncludedType.DOCUMENT_CHECKS.value
    attributes = factory.SubFactory(UbbleIdentificationIncludedDocumentChecksAttributesFactory)


class UbbleIdentificationIncludedFaceChecksFactory(UbbleIdentificationIncludedFactory):
    class Meta:
        model = ubble_fraud_models.UbbleIdentificationIncludedFaceChecks

    type = IdentificationIncludedType.FACE_CHECKS.value
    attributes = factory.SubFactory(UbbleIdentificationIncludedFaceChecksAttributesFactory)


class UbbleIdentificationIncludedReferenceDataChecksFactory(UbbleIdentificationIncludedFactory):
    class Meta:
        model = ubble_fraud_models.UbbleIdentificationIncludedReferenceDataChecks

    type = IdentificationIncludedType.REFERENCE_DATA_CHECKS.value
    attributes = factory.SubFactory(UbbleIdentificationIncludedReferenceDataChecksAttributesFactory)


class UbbleIdentificationIncludedDocFaceMatchesFactory(UbbleIdentificationIncludedFactory):
    class Meta:
        model = ubble_fraud_models.UbbleIdentificationIncludedDocFaceMatches

    type = IdentificationIncludedType.DOC_FACE_MATCHES.value
    attributes = factory.SubFactory(UbbleIdentificationIncludedDocFaceMatchesAttributesFactory)


class UbbleIdentificationResponseFactory(factory.Factory):
    class Meta:
        model = ubble_fraud_models.UbbleIdentificationResponse

    class Params:
        identification_state = IdentificationState.NEW

    data = factory.SubFactory(
        UbbleIdentificationDataFactory, identification_state=factory.SelfAttribute("..identification_state")
    )

    @factory.lazy_attribute
    def included(self):
        included_data = defaultdict(
            list,
            {
                IdentificationState.PROCESSING: [
                    UbbleIdentificationIncludedDocumentsFactory,
                ],
                IdentificationState.VALID: [
                    UbbleIdentificationIncludedDocumentsFactory,
                    UbbleIdentificationIncludedDocumentChecksFactory,
                    UbbleIdentificationIncludedFaceChecksFactory,
                    UbbleIdentificationIncludedDocFaceMatchesFactory,
                    UbbleIdentificationIncludedReferenceDataChecksFactory,
                ],
                IdentificationState.INVALID: [
                    UbbleIdentificationIncludedDocumentsFactory,
                    UbbleIdentificationIncludedDocumentChecksFactory,
                    UbbleIdentificationIncludedFaceChecksFactory,
                    UbbleIdentificationIncludedDocFaceMatchesFactory,
                    UbbleIdentificationIncludedReferenceDataChecksFactory,
                ],
                IdentificationState.UNPROCESSABLE: [
                    UbbleIdentificationIncludedDocumentsFactory,
                    UbbleIdentificationIncludedDocumentChecksFactory,
                    UbbleIdentificationIncludedFaceChecksFactory,
                    UbbleIdentificationIncludedDocFaceMatchesFactory,
                    UbbleIdentificationIncludedReferenceDataChecksFactory,
                ],
            },
        )[self.identification_state]

        included_data = [sf(identification_state=self.identification_state) for sf in included_data]
        return included_data
