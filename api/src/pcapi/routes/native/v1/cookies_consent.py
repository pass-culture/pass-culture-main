import logging

from pcapi.routes.serialization import cookies_consent as cookies_consent_serializers
from pcapi.serialization.decorator import spectree_serialize

from .. import blueprint


logger = logging.getLogger(__name__)


@blueprint.native_route("/cookies_consent", methods=["POST"])
@spectree_serialize(
    on_success_status=204,
    on_error_statuses=[400],
    api=blueprint.api,
)
def cookies_consent(body: cookies_consent_serializers.CookieConsentRequest) -> None:
    logger.info(
        "Cookies consent",
        extra={"analyticsSource": "app-native", **body.dict()},
        technical_message_id="cookies_consent",
    )
