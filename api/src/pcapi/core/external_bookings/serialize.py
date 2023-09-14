import datetime

import pydantic.v1 as pydantic_v1

import pcapi.core.bookings.models as bookings_models
import pcapi.core.finance.utils as finance_utils


class ExternalEventBookingRequest(pydantic_v1.BaseModel):
    booking_confirmation_date: datetime.datetime
    booking_creation_date: datetime.datetime
    booking_quantity: pydantic_v1.StrictInt
    offer_ean: str | None
    offer_id: pydantic_v1.StrictInt
    offer_name: str
    offer_price: pydantic_v1.StrictInt
    price_category_id: pydantic_v1.StrictInt
    price_category_label: str
    stock_id: pydantic_v1.StrictInt
    user_birth_date: datetime.date
    user_email: str
    user_first_name: str
    user_last_name: str
    user_phone: str | None
    venue_address: str
    venue_department_code: str
    venue_id: pydantic_v1.StrictInt
    venue_name: str

    @classmethod
    def build_external_booking(
        cls,
        booking: bookings_models.Booking,
    ) -> "ExternalEventBookingRequest":
        stock = booking.stock
        user = booking.user
        return cls(
            booking_confirmation_date=booking.cancellationLimitDate,  # type: ignore [arg-type]
            booking_creation_date=booking.dateCreated,
            booking_quantity=booking.quantity,
            offer_ean=stock.offer.extraData.get("ean") if stock.offer.extraData is not None else None,
            offer_id=stock.offer.id,
            offer_name=stock.offer.name,
            offer_price=finance_utils.to_eurocents(stock.priceCategory.price),
            price_category_id=stock.priceCategoryId,  # type: ignore [arg-type]
            price_category_label=stock.priceCategory.label,  # type: ignore [arg-type]
            stock_id=booking.stockId,
            user_birth_date=user.birth_date,  # type: ignore [arg-type]
            user_email=user.email,
            user_first_name=user.firstName,  # type: ignore [arg-type]
            user_last_name=user.lastName,  # type: ignore [arg-type]
            user_phone=user.phoneNumber,  # type: ignore [arg-type]
            venue_address=stock.offer.venue.address,
            venue_department_code=stock.offer.venue.departementCode,
            venue_id=stock.offer.venue.id,
            venue_name=stock.offer.venue.name,
        )


class ExternalEventTicket(pydantic_v1.BaseModel):
    barcode: str = pydantic_v1.Field(max_length=100)
    seat: str | None = pydantic_v1.Field(max_length=100)


class ExternalEventBookingResponse(pydantic_v1.BaseModel):
    tickets: list[ExternalEventTicket]
    remainingQuantity: pydantic_v1.StrictInt


class ExternalEventBookingErrorResponse(pydantic_v1.BaseModel):
    error: str
    remainingQuantity: pydantic_v1.StrictInt | None


class ExternalEventCancelBookingRequest(pydantic_v1.BaseModel):
    barcodes: list[str]

    @classmethod
    def build_external_cancel_booking(cls, barcodes: list[str]) -> "ExternalEventCancelBookingRequest":
        return cls(barcodes=barcodes)


class ExternalEventCancelBookingResponse(pydantic_v1.BaseModel):
    error: str | None
    remainingQuantity: pydantic_v1.StrictInt
