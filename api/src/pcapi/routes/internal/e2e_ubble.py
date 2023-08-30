import json
import uuid

from flask import current_app as app
from flask import redirect

from pcapi import settings
from pcapi.core.fraud.ubble import models as ubble_fraud_models
from pcapi.routes.native.v1 import blueprint
from pcapi.serialization.decorator import spectree_serialize


def ubble_identification_response_template():
    return {
        "data": {
            "type": "identifications",
            "id": "3191295",
            "attributes": {
                "score": ubble_fraud_models.UbbleScore.INVALID.value,
                "anonymized-at": None,
                "comment": None,
                "created-at": "2021-11-18T18:59:59.273402Z",
                "ended-at": None,
                "identification-id": "29d9eca4-dce6-49ed-b1b5-8bb0179493a8",
                "identification-url": "https://localhost:5001/native/v1/ubble_mock/identifications/29d9eca4-dce6-49ed-b1b5-8bb0179493a8",
                "is-live": False,
                "number-of-attempts": 1,
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
                "attributes": {"last-name": None, "first-name": None, "birth-date": "2003-10-18"},
            },
            {
                "type": "document-checks",
                "id": "4997875",
                "attributes": {
                    "data-extracted-score": ubble_fraud_models.UbbleScore.INVALID.value,
                    "expiry-date-score": ubble_fraud_models.UbbleScore.INVALID.value,
                    "issue-date-score": None,
                    "live-video-capture-score": None,
                    "mrz-validity-score": ubble_fraud_models.UbbleScore.INVALID.value,
                    "mrz-viz-score": ubble_fraud_models.UbbleScore.INVALID.value,
                    "ove-back-score": ubble_fraud_models.UbbleScore.INVALID.value,
                    "ove-front-score": ubble_fraud_models.UbbleScore.INVALID.value,
                    "ove-score": ubble_fraud_models.UbbleScore.INVALID.value,
                    "quality-score": ubble_fraud_models.UbbleScore.INVALID.value,
                    "score": ubble_fraud_models.UbbleScore.INVALID.value,
                    "supported": ubble_fraud_models.UbbleScore.INVALID.value,
                    "visual-back-score": ubble_fraud_models.UbbleScore.INVALID.value,
                    "visual-front-score": ubble_fraud_models.UbbleScore.INVALID.value,
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


@blueprint.native_v1.route("/ubble_mock/identifications/", methods=["POST"])
@spectree_serialize(on_success_status=200, api=blueprint.api)
def create_ubble_identification(data: dict) -> dict:
    """
    data = {
        "data": {
            "type": "identifications",
            "attributes": {
                "identification-form": {
                    "external-user-id": user_id,
                    "phone-number": None,
                },
                "reference-data": {
                    "first-name": first_name,
                    "last-name": last_name,
                },
                "webhook": webhook_url,
                "redirect_url": redirect_url,
            },
        }
    }
    """
    response = ubble_identification_response_template()
    user_id = data["data"]["attributes"]["identification-form"]["external-user-id"]
    configured_data = app.redis_client.get(f"ubble+{user_id}")
    identification_id = configured_data["identification-id"]
    response.update(**data)
    response["data"]["attributes"]["identification-id"] = identification_id
    response["data"]["attributes"][
        "identification-url"
    ] = f"{settings.API_URL}/native/v1/ubble_mock/{identification_id}"
    return response


@blueprint.native_v1.route("/ubble_mock/identifications/<str:identification_id>/", methods=["GET"])
@spectree_serialize(on_success_status=200, api=blueprint.api)
def get_ubble_identification(identification_id: str) -> dict:
    response = ubble_identification_response_template()
    user_id = app.redis_client.get(f"ubble+{identification_id}")
    configured_result = format_data_to_ubble_response(app.redis_client.get(f"ubble+{user_id}"))
    response.update(**configured_result)
    return response


@blueprint.native_v1.route("/ubble_mock/identifications/<str:identification_id>/redirection", methods=["GET"])
@spectree_serialize(on_success_status=200, api=blueprint.api)
def get_redirection_to_identification_end(identification_id: str) -> dict:
    user_id = app.redis_client.get(f"ubble+{identification_id}")
    configured_response = app.redis_client.get(f"ubble+{user_id}")
    redirect_url = configured_response["data"]["attributes"]["redirect-url"]
    return redirect(redirect_url, code=303)


def format_ubble_response_to_storable_data(data: dict) -> str:
    return json.dumps(data)


def format_data_to_ubble_response(data: str) -> dict:
    return json.loads(data)


def configure_identification_response(data: dict) -> str:
    user_id = data["user_id"]
    identification_id = str(uuid.uuid4())
    data["identification-id"] = identification_id
    formatted_data = format_ubble_response_to_storable_data(data)
    app.redis_client.set(f"ubble+{user_id}", formatted_data)
    app.redis_client.set(f"ubble+{identification_id}", user_id)
