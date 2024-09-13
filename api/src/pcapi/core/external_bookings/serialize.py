import datetime
import logging

import pydantic.v1 as pydantic_v1

import pcapi.core.bookings.models as bookings_models
import pcapi.core.finance.utils as finance_utils
import pcapi.core.offers.models as offers_models
import pcapi.core.users.models as users_models
from pcapi.models.feature import FeatureToggle


logger = logging.getLogger(__name__)


class ExternalEventBookingRequest(pydantic_v1.BaseModel):
    booking_confirmation_date: datetime.datetime | None
    booking_creation_date: datetime.datetime
    booking_quantity: pydantic_v1.StrictInt
    offer_ean: str | None
    offer_id: pydantic_v1.StrictInt
    offer_id_at_provider: str | None
    offer_name: str
    offer_price: pydantic_v1.StrictInt
    price_category_id: pydantic_v1.StrictInt | None
    price_category_id_at_provider: str | None
    price_category_label: str | None
    stock_id: pydantic_v1.StrictInt
    stock_id_at_provider: str | None
    user_birth_date: datetime.date
    user_email: str
    user_first_name: str
    user_last_name: str
    user_phone: str | None
    venue_address: str | None
    venue_department_code: str | None
    venue_id: pydantic_v1.StrictInt
    venue_name: str

    @classmethod
    def build_external_booking(
        cls,
        stock: offers_models.Stock,
        booking: bookings_models.Booking,
        user: users_models.User,
    ) -> "ExternalEventBookingRequest":
        if user.firstName is None:
            raise ValueError("firstName is None")
        if user.lastName is None:
            raise ValueError("lastName is None")
        price_data = (
            {
                "offer_price": finance_utils.to_eurocents(stock.priceCategory.price),
                "price_category_id": stock.priceCategoryId,
                "price_category_id_at_provider": stock.priceCategory.idAtProvider,
                "price_category_label": stock.priceCategory.label,
            }
            if stock.priceCategory
            else {"offer_price": finance_utils.to_eurocents(stock.price)}
        )

        offer_address = stock.offer.offererAddress
        if FeatureToggle.WIP_USE_OFFERER_ADDRESS_AS_DATA_SOURCE.is_active() and offer_address:
            # The label is the name of the venue, if it exists, otherwise the street is used
            address = offer_address.address.street
            venue_name = offer_address.label if offer_address.label else stock.offer.venue.name
            department_code = offer_address.address.departmentCode
        else:
            address = stock.offer.venue.street
            venue_name = stock.offer.venue.name
            department_code = stock.offer.venue.departementCode

        return cls(
            booking_confirmation_date=booking.cancellationLimitDate,
            booking_creation_date=booking.dateCreated,
            booking_quantity=booking.quantity,
            offer_ean=stock.offer.extraData.get("ean") if stock.offer.extraData is not None else None,
            offer_id=stock.offer.id,
            offer_id_at_provider=stock.offer.idAtProvider,
            offer_name=stock.offer.name,
            stock_id=booking.stockId,
            stock_id_at_provider=stock.idAtProviders,
            user_birth_date=user.birth_date,
            user_email=user.email,
            user_first_name=user.firstName,
            user_last_name=user.lastName,
            user_phone=user.phoneNumber,
            venue_address=address,
            venue_department_code=department_code,
            venue_id=stock.offer.venue.id,
            venue_name=venue_name,
            **price_data,  # type: ignore[arg-type]
        )


class ExternalEventTicket(pydantic_v1.BaseModel):
    barcode: str = pydantic_v1.Field(max_length=100)
    seat: str | None = pydantic_v1.Field(max_length=100)


class ExternalEventBookingResponse(pydantic_v1.BaseModel):
    tickets: list[ExternalEventTicket]
    remainingQuantity: int | None = pydantic_v1.Field(...)


class ExternalEventBookingErrorResponse(pydantic_v1.BaseModel):
    error: str
    remainingQuantity: int | None = pydantic_v1.Field(...)


class ExternalEventCancelBookingRequest(pydantic_v1.BaseModel):
    barcodes: list[str]

    @classmethod
    def build_external_cancel_booking(cls, barcodes: list[str]) -> "ExternalEventCancelBookingRequest":
        return cls(barcodes=barcodes)


class ExternalEventCancelBookingResponse(pydantic_v1.BaseModel):
    error: str | None
    remainingQuantity: int | None = pydantic_v1.Field(...)
