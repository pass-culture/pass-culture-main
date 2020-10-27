from typing import Dict, Optional
from pydantic import BaseModel

from pcapi.models import OfferSQLEntity, UserSQLEntity
from pcapi.core.bookings.repository import find_first_matching_from_offer_by_user
from pcapi.routes.serialization.dictifier import as_dict
from pcapi.utils.includes import (
    OFFER_INCLUDES,
    WEBAPP_GET_BOOKING_WITH_QR_CODE_INCLUDES,
)
from pcapi.serialization.utils import to_camel, dehumanize_field, humanize_field


def serialize_offer(offer: OfferSQLEntity, current_user: UserSQLEntity) -> Dict:
    dict_offer = as_dict(offer, includes=OFFER_INCLUDES)

    booking = find_first_matching_from_offer_by_user(offer.id, current_user.id)
    if booking:
        dict_offer["firstMatchingBooking"] = as_dict(
            booking, includes=WEBAPP_GET_BOOKING_WITH_QR_CODE_INCLUDES
        )

    return dict_offer


class PostOfferBodyModel(BaseModel):
    venue_id: str
    product_id: Optional[int]
    type: Optional[str]
    name: Optional[str]
    booking_email: Optional[str]

    _normalize_product_id = dehumanize_field("product_id")

    class Config:
        alias_generator = to_camel


class PostOfferResponseBodyModel(BaseModel):
    id: str

    _normalize_id = humanize_field("id")

    class Config:  # pylint: disable=too-few-public-methods
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
