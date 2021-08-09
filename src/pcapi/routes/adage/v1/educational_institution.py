import logging
from typing import Optional

from sqlalchemy.orm import joinedload

from pcapi.core.bookings.models import Booking
from pcapi.core.educational.models import EducationalBooking
from pcapi.core.educational.models import EducationalDeposit
from pcapi.core.educational.models import EducationalInstitution
from pcapi.core.educational.models import EducationalYear
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import Stock
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
    educational_institution: EducationalInstitution = EducationalInstitution.query.filter(
        EducationalInstitution.institutionId == uai_code
    ).first_or_404()

    bookings = (
        Booking.query.join(EducationalBooking)
        .join(EducationalInstitution)
        .join(EducationalYear)
        .options(joinedload(Booking.user, innerjoin=True))
        .options(
            joinedload(Booking.stock, innerjoin=True)
            .joinedload(Stock.offer, innerjoin=True)
            .joinedload(Offer.venue, innerjoin=True)
        )
        .options(
            joinedload(Booking.educationalBooking).joinedload(EducationalBooking.educationalInstitution, innerjoin=True)
        )
        .filter(EducationalInstitution.institutionId == uai_code)
        .filter(EducationalYear.adageId == year_id)
        .all()
    )

    educational_deposit: Optional[EducationalDeposit] = (
        EducationalDeposit.query.filter(EducationalDeposit.educationalYearId == year_id)
        .filter(EducationalDeposit.educationalInstitutionId == educational_institution.id)
        .one_or_none()
    )

    return EducationalInstitutionResponse(
        credit=educational_deposit.amount if educational_deposit else 0,
        isFinal=educational_deposit.isFinal if educational_deposit else False,
        prebookings=serialize_educational_bookings([booking.educationalBooking for booking in bookings]),
    )
