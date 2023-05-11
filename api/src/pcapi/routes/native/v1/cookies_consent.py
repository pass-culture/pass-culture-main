import logging

from pcapi.routes.shared import cookies_consent as serializers
from pcapi.serialization.decorator import spectree_serialize

from . import blueprint


logger = logging.getLogger(__name__)


@blueprint.native_v1.route("/cookies_consent", methods=["POST"])
@spectree_serialize(
    on_success_status=204,
    on_error_statuses=[400],
    api=blueprint.api,
)
def cookies_consent(body: serializers.CookieConsentRequest) -> None:
    logger.info(
        "Cookies consent",
        extra={"analyticsSource": "app-native", **body.dict()},
        technical_message_id="cookies_consent",
    )
