import datetime

import pydantic as pydantic_v2

from pcapi.core.bookings import models as booking_models
from pcapi.core.finance import utils as finance_utils
from pcapi.routes import serialization
from pcapi.routes.public.documentation_constants.fields_v2 import fields_v2
from pcapi.routes.public.individual_offers.v1.base_serialization import IndexPaginationQueryParamsV2
from pcapi.routes.serialization.utils import raise_error_from_location


class GetBookingResponse(serialization.HttpBodyModel):
    id: int = fields_v2.BOOKING_ID
    quantity: int = fields_v2.BOOKING_QUANTITY
    creation_date: datetime.datetime = fields_v2.BOOKING_CREATION_DATE
    confirmation_date: datetime.datetime | None = fields_v2.BOOKING_CONFIRMATION_DATE_NOT_REQUIRED
    price: int = fields_v2.PRICE
    status: booking_models.BookingStatus = fields_v2.BOOKING_STATUS

    offer_id: int = fields_v2.OFFER_ID
    stock_id: int = fields_v2.STOCK_ID
    price_category_id: int | None = fields_v2.PRICE_CATEGORY_ID_NOT_REQUIRED
    price_category_label: str | None = fields_v2.PRICE_CATEGORY_LABEL_NOT_REQUIRED
    offer_name: str = fields_v2.OFFER_NAME
    offer_ean: str | None = fields_v2.EAN_NOT_REQUIRED
    offer_address: str | None = fields_v2.OFFER_ADDRESS_NOT_REQUIRED
    offer_department_code: str | None = fields_v2.OFFER_DEPARTEMENT_CODE_NOT_REQUIRED

    venue_id: int = fields_v2.VENUE_ID
    venue_name: str = fields_v2.VENUE_PUBLIC_NAME

    user_email: str = fields_v2.USER_EMAIL
    user_phone_number: str | None = fields_v2.USER_PHONE_NUMBER_NOT_REQUIRED
    user_first_name: str | None = fields_v2.USER_FIRST_NAME_NOT_REQUIRED
    user_last_name: str | None = fields_v2.USER_LAST_NAME_NOT_REQUIRED
    user_birth_date: datetime.date | None = fields_v2.USER_BIRTH_DATE_NOT_REQUIRED
    user_postal_code: str | None = fields_v2.USER_POSTAL_CODE_NOT_REQUIRED

    @classmethod
    def build_booking(cls, booking: booking_models.Booking) -> "GetBookingResponse":
        offerer_address = booking.stock.offer.offererAddress
        price_category = booking.stock.priceCategory
        return cls(
            id=booking.id,
            creation_date=booking.dateCreated,
            confirmation_date=booking.cancellationLimitDate,
            quantity=booking.quantity,
            price=finance_utils.to_cents(booking.amount),
            status=booking.status,
            price_category_id=price_category.id if price_category else None,
            price_category_label=price_category.label if price_category else None,
            offer_id=booking.stock.offer.id,
            stock_id=booking.stock.id,
            offer_name=booking.stock.offer.name,
            # TODO bdalbianco 02/06/2025: CLEAN_OA remove check when no virtual venue
            offer_address=offerer_address.address.street if offerer_address else None,
            offer_department_code=offerer_address.address.departmentCode if offerer_address else None,
            offer_ean=booking.stock.offer.ean,
            venue_id=booking.venue.id,
            venue_name=booking.venue.name,
            user_email=booking.email,
            user_birth_date=booking.user.birth_date,
            user_first_name=booking.user.firstName,
            user_last_name=booking.user.lastName,
            user_phone_number=booking.user.phoneNumber,
            user_postal_code=booking.user.postalCode,
        )


class GetBookingsQueryParams(IndexPaginationQueryParamsV2):
    offer_id: int | None = fields_v2.OFFER_ID_NOT_REQUIRED
    venue_id: int | None = fields_v2.VENUE_ID_NOT_REQUIRED
    price_category_id: int | None = fields_v2.PRICE_CATEGORY_ID_NOT_REQUIRED
    stock_id: int | None = fields_v2.STOCK_ID_NOT_REQUIRED
    status: booking_models.BookingStatus | None = fields_v2.BOOKING_STATUS_NOT_REQUIRED
    beginning_datetime: datetime.datetime | None = fields_v2.BEGINNING_DATETIME_NOT_REQUIRED

    @pydantic_v2.model_validator(mode="after")
    def check_offer_id_or_venue_id_is_set(self) -> "GetBookingsQueryParams":
        if not self.offer_id and not self.venue_id:
            raise_error_from_location(None, "global", "`offerId` or `venueId` must be set")

        return self


class GetFilteredBookingsResponse(serialization.HttpBodyModel):
    bookings: list[GetBookingResponse]
