import logging

from pcapi.core.educational.api import find_collective_bookings_for_adage
from pcapi.core.educational.api import find_educational_deposit_by_institution_id_and_year
from pcapi.core.educational.models import EducationalInstitution
from pcapi.core.educational.repository import find_educational_institution_by_uai_code
from pcapi.models.api_errors import ApiErrors
from pcapi.routes.adage.security import adage_api_key_required
from pcapi.routes.adage.v1.serialization.educational_institution import EducationalInstitutionResponse
from pcapi.routes.adage.v1.serialization.prebooking import serialize_collective_bookings
from pcapi.serialization.decorator import spectree_serialize


logger = logging.getLogger(__name__)

from . import blueprint


educational_institution_path = "years/<string:year_id>/educational_institution/<string:uai_code>"


@blueprint.adage_v1.route(educational_institution_path, methods=["GET"])
@spectree_serialize(
    api=blueprint.api,
    response_model=EducationalInstitutionResponse,
    on_error_statuses=[404],
    tags=("get educational institution",),
)
@adage_api_key_required
def get_educational_institution(year_id: str, uai_code: str) -> EducationalInstitutionResponse:
    educational_institution: EducationalInstitution | None = find_educational_institution_by_uai_code(uai_code)

    if not educational_institution:
        raise ApiErrors({"code": "EDUCATIONAL_INSTITUTION_NOT_FOUND"}, status_code=404)

    collective_bookings = find_collective_bookings_for_adage(uai_code=uai_code, year_id=year_id)
    prebookings = serialize_collective_bookings(collective_bookings)

    educational_deposit = find_educational_deposit_by_institution_id_and_year(
        educational_year_id=year_id, educational_institution_id=educational_institution.id  # type: ignore [arg-type]
    )
    return EducationalInstitutionResponse(
        credit=educational_deposit.amount if educational_deposit else 0,
        isFinal=educational_deposit.isFinal if educational_deposit else False,
        prebookings=prebookings,
    )
