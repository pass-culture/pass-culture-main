import logging
from typing import Optional

from pcapi.core.educational.models import EducationalDeposit
from pcapi.core.educational.models import EducationalInstitution
from pcapi.core.educational.repository import find_educational_bookings_for_adage
from pcapi.core.educational.repository import find_educational_institution_by_uai_code
from pcapi.models.api_errors import ApiErrors
from pcapi.routes.adage.security import adage_api_key_required
from pcapi.routes.adage.v1.serialization.educational_institution import EducationalInstitutionResponse
from pcapi.routes.adage.v1.serialization.prebooking import serialize_educational_bookings
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
    educational_institution: Optional[EducationalInstitution] = find_educational_institution_by_uai_code(uai_code)

    if not educational_institution:
        raise ApiErrors({"code": "EDUCATIONAL_INSTITUTION_NOT_FOUND"}, status_code=404)

    educational_bookings = find_educational_bookings_for_adage(uai_code=uai_code, year_id=year_id)

    educational_deposit: Optional[EducationalDeposit] = (
        EducationalDeposit.query.filter(EducationalDeposit.educationalYearId == year_id)
        .filter(EducationalDeposit.educationalInstitutionId == educational_institution.id)
        .one_or_none()
    )

    return EducationalInstitutionResponse(
        credit=educational_deposit.amount if educational_deposit else 0,
        isFinal=educational_deposit.isFinal if educational_deposit else False,
        prebookings=serialize_educational_bookings(educational_bookings),
    )
