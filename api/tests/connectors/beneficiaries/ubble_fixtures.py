import copy
import datetime

from dateutil.relativedelta import relativedelta

from pcapi.connectors.serialization import ubble_serializers
from pcapi.utils.date import DATE_ISO_FORMAT


def build_ubble_identification_v2_response(
    status: str | None = None,
    response_codes: list[dict] | None = None,
    declared_data: dict | None = None,
    documents: list[dict] | None = None,
    birth_date: datetime.date | None = None,
    created_on: datetime.datetime | None = None,
    age_at_registration: int | None = None,
) -> dict:
    identification_response = copy.deepcopy(UBBLE_IDENTIFICATION_V2_RESPONSE)
    if status is not None:
        identification_response["status"] = status
    if response_codes is not None:
        identification_response["response_codes"] = response_codes
    if declared_data is not None:
        identification_response["declared_data"] = declared_data
    if documents is not None:
        identification_response["documents"] = documents
    if birth_date is not None and len(identification_response["documents"]) > 0:
        identification_response["documents"][0]["birth_date"] = birth_date.isoformat()
    if created_on is not None:
        identification_response["created_on"] = created_on.isoformat() + "Z"
    if age_at_registration is not None and birth_date is None:
        registration_date = datetime.datetime.strptime(identification_response["created_on"], DATE_ISO_FORMAT)
        years_before_registration = registration_date - relativedelta(years=age_at_registration, months=1)
        identification_response["documents"][0]["birth_date"] = years_before_registration.date().isoformat()
    return identification_response


UBBLE_IDENTIFICATION_V2_RESPONSE = {
    "id": "idv_01jbcfv575hfh62b6t89304769",
    "user_journey_id": "usj_02h13smebsb2y1tyyrzx1sgma7",
    "applicant_id": "aplt_02jbcfv54zmsbrrzf4g1f7qfh7",
    "webhook_url": "https://webhook.example.com",
    "redirect_url": "https://redirect.example.com",
    "declared_data": {"name": "Oriane Bertone"},
    "created_on": "2024-10-29T15:55:50.391708Z",
    "modified_on": "2024-10-30T17:01:23.856294Z",
    "status": "approved",
    "face": {"image_signed_url": "https://api.ubble.example.com/idv_01jbcfv575hfh62b6t89304769"},
    "response_codes": [{"code": 10000, "summary": "approved"}],
    "documents": [
        {
            "back_image_signed_url": "https://minio.ubble.ai/production.ubble.ai/OIOXQTAYFYMF/idv_01jbcfv575hfh62b6t89304769/3ab73828-f228-431c-ad35-520c8e877eef/5ed52248-d61d-4b91-b8aa-59d41bd0f8ad/back_id.jpeg?response-content-type=image%2Fpng&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=6nzrc5UNPR864KRwHLkZ%2F20250716%2Feu-west-2%2Fs3%2Faws4_request&X-Amz-Date=20250716T135414Z&X-Amz-Expires=600&X-Amz-SignedHeaders=host&X-Amz-Signature=cb79c6201419d7af19a61c7e94ac58e34f61ce1536de329f876fbf8f1f68b1d6",
            "birth_date": "2005-03-10",
            "birth_place": "Nice",
            "document_expiry_date": "2035-03-25",
            "document_issue_date": "2025-03-26",
            "document_issue_place": "Paris",
            "document_issuing_country": "FRA",
            "document_mrz": "P<FRASMITHJOHNDANIEL<<<<<<<<<<<<<<<<<<<<<<<<<<<<",
            "document_number": "A12345678",
            "document_type": "ID",
            "first_names": "Toby, Daniel",
            "front_image_signed_url": "https://minio.ubble.ai/production.ubble.ai/OIOXQTAYFYMF/idv_01jbcfv575hfh62b6t89304769/3ab73828-f228-431c-ad35-520c8e877eef/5ed52248-d61d-4b91-b8aa-59d41bd0f8ad/front_id.jpeg?response-content-type=image%2Fpng&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=6nzrc5UNPR864KRwHLkZ%2F20250716%2Feu-west-2%2Fs3%2Faws4_request&X-Amz-Date=20250716T135414Z&X-Amz-Expires=600&X-Amz-SignedHeaders=host&X-Amz-Signature=209dd3ab5110c752c7a9d50c9202863d32895d4b7f175f1a29849a45d6251c90",
            "full_name": "Oriane Max BERTONE",
            "gender": "F",
            "last_name": "BERTONE",
            "personal_number": "AB1234567890XY",
            "tax_identification_number": "TIN123456789",
        }
    ],
    "_links": {
        "self": {"href": "https://api.ubble.example.com/v2/identity-verifications/idv_01jbcfv575hfh62b6t89304769"},
        "applicant": {"href": "https://api.ubble.example.com/v2/applicants/aplt_01jbcfv54zmsbrrzf4g1f7qfh7"},
        "verification_url": {"href": "https://verification.ubble.example.com/"},
    },
}

UBBLE_IDENTIFICATION_RESPONSE = {
    "data": {
        "type": "identifications",
        "id": "3191295",
        "attributes": {
            "score": ubble_serializers.UbbleScore.INVALID.value,
            "anonymized-at": None,
            "comment": None,
            "created-at": "2021-11-18T18:59:59.273402Z",
            "ended-at": None,
            "identification-id": "29d9eca4-dce6-49ed-b1b5-8bb0179493a8",
            "identification-url": "https://id.ubble.ai/29d9eca4-dce6-49ed-b1b5-8bb0179493a8",
            "is-live": False,
            "number-of-attempts": 0,
            "redirect-url": "https://example.com/redirect-url",
            "started-at": None,
            "status-updated-at": "2021-11-18T18:59:59.273171Z",
            "status": "uninitiated",
            "updated-at": "2021-11-18T18:59:59.329011Z",
            "user-agent": None,
            "user-ip-address": None,
            "webhook": "https://example.com/webhook",
        },
        "relationships": {
            "identity": {
                "data": {"type": "identities", "id": "3187041"},
                "links": {"related": "https://api.example.com/api/identifications/3191295/identity"},
            },
            "reference-data": {
                "data": {"type": "reference-data", "id": "119617"},
                "links": {"related": "https://api.example.com/api/identifications/3191295/reference_data"},
            },
            "reason-codes": {
                "meta": {"count": 2},
                "data": [
                    {"type": "reason-codes", "id": "1304"},
                    {"type": "reason-codes", "id": "1310"},
                ],
            },
        },
    },
    "included": [
        {
            "type": "identities",
            "id": "3187041",
            "attributes": {"birth-date": None, "first-name": None, "last-name": None},
        },
        {
            "type": "reference-data",
            "id": "119617",
            "attributes": {"last-name": "LastName", "first-name": "FirstName", "birth-date": "2003-10-18"},
        },
        {
            "type": "document-checks",
            "id": "4997875",
            "attributes": {
                "data-extracted-score": ubble_serializers.UbbleScore.INVALID.value,
                "expiry-date-score": ubble_serializers.UbbleScore.INVALID.value,
                "issue-date-score": None,
                "live-video-capture-score": None,
                "mrz-validity-score": ubble_serializers.UbbleScore.INVALID.value,
                "mrz-viz-score": ubble_serializers.UbbleScore.INVALID.value,
                "ove-back-score": ubble_serializers.UbbleScore.INVALID.value,
                "ove-front-score": ubble_serializers.UbbleScore.INVALID.value,
                "ove-score": ubble_serializers.UbbleScore.INVALID.value,
                "quality-score": ubble_serializers.UbbleScore.INVALID.value,
                "score": ubble_serializers.UbbleScore.INVALID.value,
                "supported": ubble_serializers.UbbleScore.INVALID.value,
                "visual-back-score": ubble_serializers.UbbleScore.INVALID.value,
                "visual-front-score": ubble_serializers.UbbleScore.INVALID.value,
            },
            "relationships": {},
        },
        {
            "type": "documents",
            "id": "4998439",
            "attributes": {
                "birth-date": "2003-10-18",
                "birth-place": None,
                "document-number": "777777777777",
                "document-type": "ID",
                "document-type-detailed": None,
                "expiry-date": "2031-09-07",
                "first-name": "FirstName",
                "gender": "M",
                "issue-date": None,
                "issue-place": None,
                "issuing-state-code": "FRA",
                "last-name": "LastName",
                "married-name": None,
                "media-type": "video",
                "mrz": "MRZ",
                "nationality": None,
                "obtaining-date": None,
                "personal-number": None,
                "remarks": None,
            },
            "relationships": {},
        },
    ],
}
