import enum

import pydantic

from pcapi.core.bookings import models as booking_models
from pcapi.core.finance import utils as finance_utils
from pcapi.routes import serialization
from pcapi.utils import date as date_utils


class StrEnum(str, enum.Enum):
    # StrEnum is needed so that swagger ui displays the enum values
    # see https://github.com/swagger-api/swagger-ui/issues/6906
    pass


class GetBookingResponse(serialization.ConfiguredBaseModel):
    id: int
    quantity: int
    creation_date: str
    confirmation_date: str | None = pydantic.Field(
        description="For event offers, deadline for cancellation by the beneficiary."
    )
    price: pydantic.StrictInt

    offer_id: int
    stock_id: int
    price_category_id: int | None
    price_category_label: str | None
    offer_name: str
    offer_ean: str | None

    venue_id: int
    venue_name: str
    venue_address: str
    venue_departement_code: str

    user_email: str
    user_birth_date: str | None

    @classmethod
    def build_booking(cls, booking: booking_models.Booking) -> "GetBookingResponse":
        extra_data = booking.stock.offer.extraData or {}
        birth_date = date_utils.isoformat(booking.user.birth_date) if booking.user.birth_date else None  # type: ignore [arg-type]
        return cls(
            id=booking.id,
            creation_date=date_utils.format_into_utc_date(booking.dateCreated),
            confirmation_date=date_utils.format_into_utc_date(booking.cancellationLimitDate),  # type: ignore [arg-type]
            quantity=booking.quantity,
            price=finance_utils.to_eurocents(booking.amount),
            price_category_id=booking.stock.priceCategory.id if booking.stock.priceCategory else None,
            price_category_label=booking.stock.priceCategory.label if booking.stock.priceCategory else None,  # type: ignore [arg-type]
            offer_id=booking.stock.offer.id,
            stock_id=booking.stock.id,
            offer_name=booking.stock.offer.name,
            offer_ean=extra_data.get("ean"),
            venue_id=booking.venue.id,
            venue_name=booking.venue.name,
            venue_address=booking.venue.address,
            venue_departement_code=booking.venue.departementCode,
            user_email=booking.email,
            user_birth_date=birth_date,
        )
