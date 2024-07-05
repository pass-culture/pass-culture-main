import pydantic.v1 as pydantic_v1

from pcapi.core.providers import models as providers_models
from pcapi.routes import serialization
from pcapi.routes.public.documentation_constants.fields import fields


class ProviderResponse(serialization.ConfiguredBaseModel):
    id: int = fields.PROVIDER_ID
    name: str = fields.PROVIDER_NAME

    # External urls
    logo_url: str | None = fields.PROVIDER_LOGO_URL
    notification_url: str | None = fields.PROVIDER_NOTIFICATION_URL
    booking_url: str | None = fields.PROVIDER_BOOKING_URL
    cancel_url: str | None = fields.PROVIDER_CANCEL_URL

    @classmethod
    def build_model(cls, provider: providers_models.Provider) -> "ProviderResponse":
        return cls(
            id=provider.id,
            name=provider.name,
            logo_url=provider.logoUrl,
            notification_url=provider.notificationExternalUrl,
            booking_url=provider.bookingExternalUrl,
            cancel_url=provider.cancelExternalUrl,
        )


class ProviderUpdate(serialization.ConfiguredBaseModel):
    notification_url: pydantic_v1.HttpUrl | None = fields.PROVIDER_NOTIFICATION_URL
    booking_url: pydantic_v1.HttpUrl | None = fields.PROVIDER_BOOKING_URL
    cancel_url: pydantic_v1.HttpUrl | None = fields.PROVIDER_CANCEL_URL


class VenueProviderExternalUrlsUpdate(serialization.ConfiguredBaseModel):
    notification_url: pydantic_v1.HttpUrl | None = fields.PROVIDER_NOTIFICATION_URL
    booking_url: pydantic_v1.HttpUrl | None = fields.PROVIDER_BOOKING_URL
    cancel_url: pydantic_v1.HttpUrl | None = fields.PROVIDER_CANCEL_URL
