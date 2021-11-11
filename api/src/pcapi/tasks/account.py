from pydantic import BaseModel

from pcapi import settings
from pcapi.connectors.beneficiaries.id_check_middleware import IdCheckMiddlewareException
from pcapi.core.users import api
from pcapi.core.users import exceptions
from pcapi.models import ApiErrors
from pcapi.tasks.decorator import task


ID_CHECK_TASK_QUEUE = settings.GCP_ID_CHECK_CLOUD_TASK_NAME


class VerifyIdentityDocumentRequest(BaseModel):
    image_storage_path: str


@task(ID_CHECK_TASK_QUEUE, "/verify_identity_document")
def verify_identity_document(payload: VerifyIdentityDocumentRequest) -> None:
    try:
        api.verify_identity_document_informations(payload.image_storage_path)
        return
    except (exceptions.IdentityDocumentVerificationException, IdCheckMiddlewareException):
        raise ApiErrors(status_code=503)
