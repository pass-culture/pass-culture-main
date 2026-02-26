import datetime

from pydantic import BaseModel as BaseModelV2

from pcapi.core.bookings import models as bookings_models
from pcapi.core.finance import utils as finance_utils
from pcapi.core.offers import models as offers_models
from pcapi.core.offers.utils import get_offer_address
from pcapi.core.users import models as users_models


class ExternalEventBookingRequest(BaseModelV2):
    booking_confirmation_date: datetime.datetime | None
    booking_creation_date: datetime.datetime
    booking_quantity: int
    offer_ean: str | None
    offer_id: int
    offer_id_at_provider: str | None
    offer_name: str
    offer_price: int
    price_category_id: int | None
    price_category_id_at_provider: str | None
    price_category_label: str | None
    stock_id: int
    stock_id_at_provider: str | None
    user_birth_date: datetime.date
    user_email: str
    user_first_name: str
    user_last_name: str
    user_phone: str | None
    venue_address: str | None
    venue_department_code: str | None
    venue_id: int
    venue_name: str

    @classmethod
    def build_external_booking(
        cls,
        stock: offers_models.Stock,
        booking: bookings_models.Booking,
        user: users_models.User,
    ) -> "ExternalEventBookingRequest":
        if user.birth_date is None:
            raise ValueError("birth_date is None")
        if user.firstName is None:
            raise ValueError("firstName is None")
        if user.lastName is None:
            raise ValueError("lastName is None")
        if stock.priceCategory:
            offer_price = finance_utils.to_cents(stock.priceCategory.price)
            price_category_id = stock.priceCategoryId
            price_category_id_at_provider = stock.priceCategory.idAtProvider
            price_category_label = stock.priceCategory.label
        else:
            offer_price = finance_utils.to_cents(stock.price)
            price_category_id = None
            price_category_id_at_provider = None
            price_category_label = None

        offer_address = get_offer_address(stock.offer)

        return cls(
            booking_confirmation_date=booking.cancellationLimitDate,
            booking_creation_date=booking.dateCreated,
            booking_quantity=booking.quantity,
            offer_ean=stock.offer.ean,
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
            venue_address=offer_address.street,
            venue_department_code=offer_address.departmentCode,
            venue_id=stock.offer.venue.id,
            venue_name=offer_address.label,
            offer_price=offer_price,
            price_category_id=price_category_id,
            price_category_id_at_provider=price_category_id_at_provider,
            price_category_label=price_category_label,
        )
