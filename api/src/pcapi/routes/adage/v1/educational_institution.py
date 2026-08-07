import logging

from pcapi.core.educational import repository
from pcapi.core.educational.serialization import collective_booking as collective_booking_serialize
from pcapi.models.api_errors import ApiErrors
from pcapi.routes.adage.security import adage_api_key_required
from pcapi.routes.adage.v1.serialization import educational_institution as educational_institution_serialization
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
    response_model=educational_institution_serialization.EducationalInstitutionResponse,
    on_error_statuses=[404],
    tags=("get educational institution",),
)
def get_educational_institution(
    year_id: str, uai_code: str
) -> educational_institution_serialization.EducationalInstitutionResponse:
    educational_institution = repository.find_educational_institution_by_uai_code(uai_code)

    if not educational_institution:
        raise ApiErrors({"code": "EDUCATIONAL_INSTITUTION_NOT_FOUND"}, status_code=404)

    collective_bookings = repository.find_collective_bookings_for_adage(uai_code=uai_code, year_id=year_id)
    prebookings = collective_booking_serialize.serialize_collective_bookings(collective_bookings)

    educational_deposits = repository.find_educational_deposits_by_institution_id_and_year(
        educational_year_id=year_id, educational_institution_id=educational_institution.id
    )

    return educational_institution_serialization.EducationalInstitutionResponse(
        prebookings=prebookings,
        deposits=[
            educational_institution_serialization.EducationalInstitutionDepositResponse.build(deposit)
            for deposit in educational_deposits
        ],
    )
