from flask_login import current_user
from flask_login import login_required

from pcapi.core.pro_assistant import api as pro_assistant_api
from pcapi.core.pro_assistant import exceptions as pro_assistant_exceptions
from pcapi.models.api_errors import ApiErrors
from pcapi.models.feature import FeatureToggle
from pcapi.routes.pro.blueprint import pro_blueprint
from pcapi.routes.serialization import pro_assistant_serialize
from pcapi.serialization.decorator import spectree_serialize
from pcapi.utils.feature import feature_required
from pcapi.utils.rest import check_user_has_access_to_offerer
from pcapi.utils.transaction_manager import atomic

from . import blueprint


@pro_blueprint.route("/assistant/messages", methods=["POST"])
@atomic()
@login_required
@feature_required(FeatureToggle.WIP_ENABLE_PRO_ASSISTANT)
@spectree_serialize(
    response_model=pro_assistant_serialize.PostProAssistantMessageResponseModel,
    api=blueprint.pro_schema,
    on_error_statuses=[400, 403, 404, 424, 429],
)
def post_pro_assistant_message(
    body: pro_assistant_serialize.PostProAssistantMessageBodyModel,
) -> pro_assistant_serialize.PostProAssistantMessageResponseModel:
    if body.offerer_id is not None:
        check_user_has_access_to_offerer(current_user, body.offerer_id)

    try:
        answer = pro_assistant_api.ask(
            user_id=current_user.id,
            offerer_id=body.offerer_id,
            conversation_id=body.conversation_id,
            message=body.message,
            current_path=body.current_path,
        )
    except pro_assistant_exceptions.ProAssistantRateLimited:
        raise ApiErrors(
            errors={"global": "Vous avez posé beaucoup de questions. Merci de réessayer un peu plus tard."},
            status_code=429,
        )
    except pro_assistant_exceptions.ConversationTooLong:
        raise ApiErrors(
            errors={"global": "Cette conversation est terminée. Commencez une nouvelle conversation."},
            status_code=400,
        )
    except pro_assistant_exceptions.ProAssistantUnavailable:
        # Not a 503: the pro portal redirects every 502/503 response to the maintenance page
        raise ApiErrors(
            errors={"global": "L'assistant est momentanément indisponible. Merci de réessayer plus tard."},
            status_code=424,
        )

    return pro_assistant_serialize.PostProAssistantMessageResponseModel.model_validate(answer)
