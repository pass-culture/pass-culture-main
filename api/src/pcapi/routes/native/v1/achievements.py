import logging

from flask_login import current_user

from pcapi.core.achievements import api as achievements_api
from pcapi.core.achievements import exceptions as achievements_exceptions
from pcapi.models.api_errors import ApiErrors
from pcapi.routes.native.security import authenticated_and_active_user_required
from pcapi.routes.native.v1.serialization import achievements as serialization
from pcapi.serialization.decorator import spectree_serialize
from pcapi.utils.transaction_manager import atomic

from .. import blueprint


logger = logging.getLogger(__name__)


@blueprint.native_route("/achievements/mark_as_seen", methods=["POST"])
@spectree_serialize(api=blueprint.api, response_model=serialization.AchievementsResponse)
@authenticated_and_active_user_required
@atomic()
def mark_achievements_as_seen(body: serialization.MarkAchievementsAsSeenRequest) -> serialization.AchievementsResponse:
    try:
        achievements_api.mark_achievements_as_seen(current_user, body.achievement_ids)
    except achievements_exceptions.AchievementNotFound:
        raise ApiErrors({"code": "ACHIEVEMENT_NOT_FOUND"}, status_code=404)

    return serialization.AchievementsResponse(
        __root__=[serialization.AchievementResponse.from_orm(achievement) for achievement in current_user.achievements]
    )
