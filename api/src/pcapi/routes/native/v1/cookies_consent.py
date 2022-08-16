import logging

from pcapi.serialization.decorator import spectree_serialize

from . import blueprint
from .serialization import cookies_consent as serializers


logger = logging.getLogger(__name__)


@blueprint.native_v1.route("/cookies_consent", methods=["POST"])
@spectree_serialize(
    on_success_status=204,
    on_error_statuses=[400],
    api=blueprint.api,
)
def cookies_consent(body: serializers.CookieConsentRequest) -> None:
    logger.info("Cookies consent", extra=body.dict())
