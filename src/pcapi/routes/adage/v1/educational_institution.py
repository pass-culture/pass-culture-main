import logging

from pcapi.routes.adage.security import adage_api_key_required
from pcapi.routes.adage.v1.serialization.educational_institution import EducationalInstitutionResponse
from pcapi.serialization.decorator import spectree_serialize


logger = logging.getLogger(__name__)

from . import blueprint


educational_institution_path = "years/<int:year_id>/educational_institution/<string:uai_code>"


@blueprint.adage_v1.route(educational_institution_path, methods=["GET"])
@spectree_serialize(
    api=blueprint.api,
    response_model=EducationalInstitutionResponse,
    on_error_statuses=[404],
    tags=("get educational institution",),
)
@adage_api_key_required
def get_educational_institution() -> EducationalInstitutionResponse:
    """Get educational instutition details and credits.

    This endpoint retrieve up-to-date credits of an educational institution for a precise year.
    """
