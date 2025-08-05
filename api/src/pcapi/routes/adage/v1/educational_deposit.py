import logging

from pcapi.core.educational.repository import get_educational_deposits_by_year
from pcapi.models.api_errors import ApiErrors
from pcapi.routes.adage.security import adage_api_key_required
from pcapi.routes.adage.v1 import blueprint
from pcapi.routes.adage.v1.serialization import educational_deposit as deposit_serialization
from pcapi.serialization.decorator import spectree_serialize
from pcapi.utils.transaction_manager import atomic


logger = logging.getLogger(__name__)


@blueprint.adage_v1.route("years/<string:year_id>/deposits", methods=["GET"])
@atomic()
@spectree_serialize(api=blueprint.api, response_model=deposit_serialization.EducationalDepositsResponse)
@adage_api_key_required
def get_educational_deposit(year_id: str) -> deposit_serialization.EducationalDepositsResponse:
    educational_deposits = get_educational_deposits_by_year(year_id=year_id)

    if not educational_deposits:
        raise ApiErrors(errors={"code": "EDUCATIONAL_DEPOSIT_NOT_FOUND"}, status_code=404)

    result = deposit_serialization.EducationalDepositsResponse(
        deposits=deposit_serialization.serialize_educational_deposits(educational_deposits)
    )
    return result
