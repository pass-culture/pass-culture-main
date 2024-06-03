from datetime import datetime
import enum

import pydantic.v1 as pydantic_v1

from pcapi.core.bookings import models as booking_models
from pcapi.core.finance import utils as finance_utils
from pcapi.routes import serialization
from pcapi.routes.public.individual_offers.v1.base_serialization import IndexPaginationQueryParams
from pcapi.utils import date as date_utils


class StrEnum(str, enum.Enum):
    # StrEnum is needed so that swagger ui displays the enum values
    # see https://github.com/swagger-api/swagger-ui/issues/6906
    pass


class GetBookingResponse(serialization.ConfiguredBaseModel):
    id: int
    quantity: int
    creation_date: str
    confirmation_date: str | None = pydantic_v1.Field(
        description="For event offers, deadline for cancellation by the beneficiary."
    )
    price: pydantic_v1.StrictInt
    status: booking_models.BookingStatus

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
    user_phone_number: str | None
    user_first_name: str | None
    user_last_name: str | None
    user_birth_date: str | None
    user_postal_code: str | None

    @classmethod
    def build_booking(cls, booking: booking_models.Booking) -> "GetBookingResponse":
        extra_data = booking.stock.offer.extraData or {}
        birth_date = date_utils.isoformat(booking.user.birth_date) if booking.user.birth_date else None
        return cls(
            id=booking.id,
            creation_date=date_utils.format_into_utc_date(booking.dateCreated),
            confirmation_date=(
                date_utils.format_into_utc_date(booking.cancellationLimitDate)
                if booking.cancellationLimitDate
                else None
            ),
            quantity=booking.quantity,
            price=finance_utils.to_eurocents(booking.amount),
            status=booking.status,
            price_category_id=booking.stock.priceCategory.id if booking.stock.priceCategory else None,
            price_category_label=booking.stock.priceCategory.label if booking.stock.priceCategory else None,  # type: ignore[arg-type]
            offer_id=booking.stock.offer.id,
            stock_id=booking.stock.id,
            offer_name=booking.stock.offer.name,
            offer_ean=extra_data.get("ean"),
            venue_id=booking.venue.id,
            venue_name=booking.venue.name,
            venue_address=booking.venue.street,
            venue_departement_code=booking.venue.departementCode,  # type: ignore[arg-type]
            user_email=booking.email,
            user_birth_date=birth_date,
            user_first_name=booking.user.firstName,
            user_last_name=booking.user.lastName,
            user_phone_number=booking.user.phoneNumber,
            user_postal_code=booking.user.postalCode,
        )


class GetFilteredBookingsRequest(IndexPaginationQueryParams):
    offer_id: int = pydantic_v1.Field(description="Id of the bookings' offer.")
    price_category_id: int | None = pydantic_v1.Field(description="Price category of the bookings' stock.")
    stock_id: int | None = pydantic_v1.Field(description="Id of the bookings' stock.")
    status: booking_models.BookingStatus | None = pydantic_v1.Field(
        description="Booking Status.\n\n* `CONFIRMED`: The bookings is confirmed.\n* `USED`: The bookings has been used.\n* `CANCELLED`: The bookings has been cancelled.\n* `REIMBURSED` The bookings has been reimbursed."
    )
    beginning_datetime: datetime | None = pydantic_v1.Field(description="Timezone aware datetime of the event.")


class GetFilteredBookingsResponse(serialization.ConfiguredBaseModel):
    bookings: list[GetBookingResponse]
