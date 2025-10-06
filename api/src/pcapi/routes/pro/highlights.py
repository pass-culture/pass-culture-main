import logging

from flask_login import login_required

from pcapi.core.highlights import repository as highlight_repository
from pcapi.routes.apis import private_api
from pcapi.routes.serialization import highlight_serialize
from pcapi.serialization.decorator import spectree_serialize
from pcapi.utils.transaction_manager import atomic

from . import blueprint


logger = logging.getLogger(__name__)


@private_api.route("/highlights", methods=["GET"])
@login_required
@spectree_serialize(
    response_model=highlight_serialize.HighlightsResponseModel,
    api=blueprint.pro_private_schema,
)
@atomic()
def get_highlights() -> highlight_serialize.HighlightsResponseModel:
    return highlight_serialize.HighlightsResponseModel(
        __root__=[
            highlight_serialize.HighlightResponseModel.from_orm(highlight)
            for highlight in highlight_repository.get_available_highlights()
        ]
    )
