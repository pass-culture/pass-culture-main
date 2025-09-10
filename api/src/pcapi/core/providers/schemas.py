import decimal

import pydantic.v1

from pcapi.routes.serialization import BaseModel


class PostVenueProviderBody(BaseModel):
    venueId: int
    providerId: int
    venueIdAtOfferProvider: str | None
    price: decimal.Decimal | None
    # absent/ignored for regular providers, required for cinema-related providers
    isDuo: bool | None
    quantity: int | None
    isActive: bool | None

    @pydantic.v1.validator("price")
    def price_must_be_positive(cls, value: decimal.Decimal | None) -> decimal.Decimal | None:
        if not value:
            return value
        if value < 0:
            raise ValueError("Le prix doit être positif.")
        return value
