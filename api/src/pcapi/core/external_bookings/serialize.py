import datetime

import pydantic

import pcapi.core.bookings.models as bookings_models
import pcapi.core.finance.utils as finance_utils
import pcapi.core.offers.models as offers_models
import pcapi.core.users.models as users_models


class ExternalEventBookingRequest(pydantic.BaseModel):
    booking_confirmation_date: datetime.datetime
    booking_creation_date: datetime.datetime
    booking_quantity: pydantic.StrictInt
    offer_ean: str | None
    offer_id: pydantic.StrictInt
    offer_name: str
    offer_price: pydantic.StrictInt
    price_category_id: pydantic.StrictInt
    price_category_label: str
    stock_id: pydantic.StrictInt
    user_birth_date: datetime.date
    user_email: str
    user_first_name: str
    user_last_name: str
    user_phone: str | None
    venue_address: str
    venue_department_code: str
    venue_id: pydantic.StrictInt
    venue_name: str

    @classmethod
    def build_external_booking(
        cls,
        stock: offers_models.Stock,
        booking: bookings_models.Booking,
        user: users_models.User,
    ) -> "ExternalEventBookingRequest":
        return cls(
            booking_confirmation_date=booking.cancellationLimitDate,
            booking_creation_date=booking.dateCreated,
            booking_quantity=booking.quantity,
            offer_ean=stock.offer.extraData.get("ean") if stock.offer.extraData is not None else None,
            offer_id=stock.offer.id,
            offer_name=stock.offer.name,
            offer_price=finance_utils.to_eurocents(stock.priceCategory.price),
            price_category_id=stock.priceCategoryId,
            price_category_label=stock.priceCategory.label,
            stock_id=booking.stockId,
            user_birth_date=user.birth_date,
            user_email=user.email,
            user_first_name=user.firstName,
            user_last_name=user.lastName,
            user_phone=user.phoneNumber,
            venue_address=stock.offer.venue.address,
            venue_department_code=stock.offer.venue.departementCode,
            venue_id=stock.offer.venue.id,
            venue_name=stock.offer.venue.name,
        )


class ExternalEventTicket(pydantic.BaseModel):
    barcode: str
    seat: str | None


class ExternalEventBookingResponse(pydantic.BaseModel):
    tickets: list[ExternalEventTicket]
    remainingQuantity: pydantic.StrictInt | None
