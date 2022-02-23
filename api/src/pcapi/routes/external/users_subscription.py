import logging

from pcapi.core.fraud.ubble import api as ubble_fraud_api
from pcapi.core.subscription.dms import api as dms_subscription_api
from pcapi.core.subscription.ubble import api as ubble_subscription_api
from pcapi.models.api_errors import ApiErrors
from pcapi.routes.apis import public_api
from pcapi.serialization.decorator import spectree_serialize
from pcapi.validation.routes import dms as dms_validation
from pcapi.validation.routes import ubble as ubble_validation


logger = logging.getLogger(__name__)


@public_api.route("/webhooks/dms/application_status", methods=["POST"])
@dms_validation.require_dms_token
@spectree_serialize(on_success_status=204, json_format=False)
def dms_webhook_update_application_status(form: dms_validation.DMSWebhookRequest) -> None:
    dms_subscription_api.parse_and_handle_dms_application(form.dossier_id, form.procedure_id)


@public_api.route("/webhooks/ubble/application_status", methods=["POST"])
@ubble_validation.require_ubble_signature
@spectree_serialize(
    headers=ubble_validation.WebhookRequestHeaders,
    on_success_status=200,
    response_model=ubble_validation.WebhookDummyReponse,
)
def ubble_webhook_update_application_status(
    body: ubble_validation.WebhookRequest,
) -> ubble_validation.WebhookDummyReponse:
    logger.info("Ubble webhook called", extra={"identification_id": body.identification_id, "status": str(body.status)})

    fraud_check = ubble_fraud_api.get_ubble_fraud_check(body.identification_id)
    if not fraud_check:
        raise ValueError(f"no Ubble fraud check found with identification_id {body.identification_id}")

    try:
        ubble_subscription_api.update_ubble_workflow(fraud_check, body.status)
    except Exception:
        logger.exception(
            "Could not update Ubble workflow",
            extra={"identitfication_id": body.identification_id, "user_id": fraud_check.userId},
        )
        raise ApiErrors({"msg": "an error occured during workflow update"}, status_code=500)

    return ubble_validation.WebhookDummyReponse()
