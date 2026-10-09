import logging

from pcapi.core.educational import repository
from pcapi.core.educational.serialization.collective_booking import serialize_collective_booking
from pcapi.models.api_errors import ApiErrors
from pcapi.routes.adage.security import adage_api_key_required
from pcapi.routes.adage.v1.serialization.educational_institution import EducationalInstitutionResponse
from pcapi.routes.adage.v1.serialization.educational_institution import serialize_deposit
from pcapi.serialization.decorator import spectree_serialize
from pcapi.utils.transaction_manager import atomic

from . import blueprint


logger = logging.getLogger(__name__)

educational_institution_path = "years/<string:year_id>/educational_institution/<string:uai_code>"


@blueprint.adage_v1.route(educational_institution_path, methods=["GET"])
@atomic()
@adage_api_key_required
@spectree_serialize(
    api=blueprint.api,
    response_model=EducationalInstitutionResponse,
    on_error_statuses=[404],
    tags=("get educational institution",),
)
def get_educational_institution(year_id: str, uai_code: str) -> EducationalInstitutionResponse:
    educational_institution = repository.find_educational_institution_by_uai_code(uai_code)

    if not educational_institution:
        raise ApiErrors({"code": "EDUCATIONAL_INSTITUTION_NOT_FOUND"}, status_code=404)

    collective_bookings = repository.find_collective_bookings_for_adage(uai_code=uai_code, year_id=year_id)

    educational_deposits = repository.find_educational_deposits_by_institution_id_and_year(
        educational_year_id=year_id, educational_institution_id=educational_institution.id
    )

    return EducationalInstitutionResponse(
        prebookings=[serialize_collective_booking(collective_booking) for collective_booking in collective_bookings],
        deposits=[serialize_deposit(deposit) for deposit in educational_deposits],
    )
