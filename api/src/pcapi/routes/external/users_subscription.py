import logging

from pcapi.connectors.dms import api as dms_connector_api
from pcapi.core.fraud.exceptions import IncompatibleFraudCheckStatus
from pcapi.core.fraud.models import FraudCheckStatus
from pcapi.core.fraud.ubble import api as ubble_fraud_api
from pcapi.core.subscription.dms import api as dms_subscription_api
from pcapi.core.subscription.exceptions import BeneficiaryFraudCheckMissingException
from pcapi.core.subscription.ubble import api as ubble_subscription_api
from pcapi.core.subscription.ubble import exceptions as ubble_exceptions
from pcapi.models.api_errors import ApiErrors
from pcapi.routes.apis import public_api
from pcapi.serialization.decorator import spectree_serialize
from pcapi.utils import requests as requests_utils
from pcapi.validation.routes import dms as dms_validation
from pcapi.validation.routes import ubble as ubble_validation


logger = logging.getLogger(__name__)


@public_api.route("/webhooks/dms/application_status", methods=["POST"])
@dms_validation.require_dms_token
@spectree_serialize(on_success_status=204, json_format=False)
def dms_webhook_update_application_status(form: dms_validation.DMSWebhookRequest) -> None:
    dms_application = dms_connector_api.DMSGraphQLClient().get_single_application_details(form.dossier_id)
    dms_subscription_api.handle_dms_application(dms_application)


@public_api.route("/webhooks/ubble/application_status", methods=["POST"])
@ubble_validation.require_ubble_signature
@spectree_serialize(
    headers=ubble_validation.WebhookRequestHeaders,  # type: ignore [arg-type]
    on_success_status=200,
    response_model=ubble_validation.WebhookDummyReponse,  # type: ignore [arg-type]
)
def ubble_webhook_update_application_status(
    body: ubble_validation.WebhookRequest,
) -> ubble_validation.WebhookDummyReponse:
    log_extra_data = {"identification_id": body.identification_id, "status": str(body.status)}
    logger.info("Ubble webhook called", extra=log_extra_data)

    fraud_check = ubble_fraud_api.get_ubble_fraud_check(body.identification_id)
    if not fraud_check:
        raise ValueError(f"no Ubble fraud check found with identification_id {body.identification_id}")

    finished_status = [FraudCheckStatus.OK, FraudCheckStatus.KO, FraudCheckStatus.CANCELED, FraudCheckStatus.SUSPICIOUS]
    if fraud_check.status in finished_status:
        logger.warning("Ubble fraud check already has finished status", extra=log_extra_data)
        return ubble_validation.WebhookDummyReponse()

    try:
        ubble_subscription_api.update_ubble_workflow(fraud_check)

    except requests_utils.ExternalAPIException as exc:
        logger.warning("External API error when updating ubble workflow", extra=log_extra_data | {"exception": exc})
        raise ApiErrors({"msg": "an error occured while fetching data"}, status_code=500)

    except Exception:
        logger.exception("Could not update Ubble workflow", extra=log_extra_data)
        raise ApiErrors({"msg": "an error occured during workflow update"}, status_code=500)

    return ubble_validation.WebhookDummyReponse()


@public_api.route("/webhooks/ubble/store_id_pictures", methods=["POST"])
@spectree_serialize(
    on_success_status=200,
    response_model=ubble_validation.WebhookDummyReponse,  # type: ignore [arg-type]
)
def ubble_webhook_store_id_pictures(
    body: ubble_validation.WebhookStoreIdPicturesRequest,
) -> ubble_validation.WebhookDummyReponse:
    logger.info("Webhook store id pictures called ", extra={"identification_id": body.identification_id})
    try:
        ubble_subscription_api.archive_ubble_user_id_pictures(body.identification_id)
    except requests_utils.ExternalAPIException as err:
        raise ApiErrors({"err": str(err)}, status_code=503 if err.is_retryable else 500)
    except ubble_exceptions.UbbleDownloadedFileEmpty as err:
        raise ApiErrors({"err": str(err)}, status_code=500)
    except BeneficiaryFraudCheckMissingException as err:
        raise ApiErrors({"err": str(err)}, status_code=404)
    except IncompatibleFraudCheckStatus as err:
        raise ApiErrors({"err": str(err)}, status_code=422)

    return ubble_validation.WebhookDummyReponse()
