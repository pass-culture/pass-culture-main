import pydantic as pydantic_v2

from pcapi.core.providers import models as providers_models
from pcapi.routes import serialization
from pcapi.routes.public.documentation_constants.fields_v2 import fields_v2


class ProviderResponse(serialization.HttpBodyModel):
    id: int = fields_v2.PROVIDER_ID
    name: str = fields_v2.PROVIDER_NAME

    # External urls
    logo_url: str | None = fields_v2.PROVIDER_LOGO_URL_NOT_REQUIRED
    notification_url: str | None = fields_v2.PROVIDER_NOTIFICATION_URL_NOT_REQUIRED
    booking_url: str | None = fields_v2.PROVIDER_BOOKING_URL_NOT_REQUIRED
    cancel_url: str | None = fields_v2.PROVIDER_CANCEL_URL_NOT_REQUIRED

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


class ProviderUpdate(serialization.HttpBodyModel):
    notification_url: pydantic_v2.HttpUrl | None = fields_v2.PROVIDER_NOTIFICATION_URL_NOT_REQUIRED
    booking_url: pydantic_v2.HttpUrl | None = fields_v2.PROVIDER_BOOKING_URL_NOT_REQUIRED
    cancel_url: pydantic_v2.HttpUrl | None = fields_v2.PROVIDER_CANCEL_URL_NOT_REQUIRED


class VenueProviderExternalUrlsUpdate(serialization.HttpBodyModel):
    notification_url: pydantic_v2.HttpUrl | None = fields_v2.PROVIDER_NOTIFICATION_URL_NOT_REQUIRED
    booking_url: pydantic_v2.HttpUrl | None = fields_v2.PROVIDER_BOOKING_URL_NOT_REQUIRED
    cancel_url: pydantic_v2.HttpUrl | None = fields_v2.PROVIDER_CANCEL_URL_NOT_REQUIRED
