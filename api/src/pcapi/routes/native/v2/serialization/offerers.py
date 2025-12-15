import pydantic as pydantic_v2

from pcapi.connectors.serialization import acceslibre_serializers
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offerers.schemas import SocialMedia
from pcapi.routes.serialization import HttpBodyModel


class VenueContact(HttpBodyModel):
    email: str | None
    phone_number: str | None
    social_medias: dict[SocialMedia, pydantic_v2.HttpUrl] | None
    website: str | None


class MotorDisability(HttpBodyModel):
    facilities: str
    exterior: str
    entrance: str
    parking: str


class AudioDisability(HttpBodyModel):
    deafAndHardOfHearing: list[str]


class VisualDisability(HttpBodyModel):
    soundBeacon: str
    audioDescription: list[str]


class MentalDisability(HttpBodyModel):
    trainedPersonnel: str


class AccessibilityData(HttpBodyModel):
    isAccessibleMotorDisability: bool
    isAccessibleAudioDisability: bool
    isAccessibleVisualDisability: bool
    isAccessibleMentalDisability: bool
    audioDisability: AudioDisability
    mentalDisability: MentalDisability
    motorDisability: MotorDisability
    visualDisability: VisualDisability


class VenueResponse(HttpBodyModel):
    id: int
    activity: offerers_models.Activity | None
    accessibility_data: AccessibilityData | None = None
    accessibility_url: str | None = None
    banner_credit: str | None = None
    banner_is_from_google: bool = False
    banner_url: pydantic_v2.HttpUrl | None
    contact: VenueContact | None
    city: str | None
    description: str | None
    is_open_to_public: bool
    is_permanent: bool
    name: str
    opening_hours: dict | None
    postal_code: str | None
    street: str | None
    timezone: str
    withdrawal_details: str | None

    @classmethod
    def build(cls, venue: offerers_models.Venue) -> "VenueResponse":
        accessibility_data = None
        accessibility_url = None
        banner_credit = None
        banner_is_from_google = False
        if venue.accessibilityProvider:
            accessibility_data = AccessibilityData.model_validate(
                acceslibre_serializers.ExternalAccessibilityDataModel.from_accessibility_infos(
                    venue.accessibilityProvider.externalAccessibilityData
                ),
            )
            accessibility_url = venue.accessibilityProvider.externalAccessibilityUrl

        if venue.bannerMeta:
            banner_credit = venue.bannerMeta.get("image_credit")
            banner_is_from_google = venue.bannerMeta.get("is_from_google", False)

        return cls(
            id=venue.id,
            accessibility_data=accessibility_data,
            accessibility_url=accessibility_url,
            activity=venue.activity,
            banner_credit=banner_credit,
            banner_is_from_google=banner_is_from_google,
            banner_url=venue.bannerUrl,
            city=venue.offererAddress.address.city,
            contact=VenueContact.model_validate(venue.contact) if venue.contact else None,
            description=venue.description,
            is_open_to_public=venue.isOpenToPublic,
            is_permanent=venue.isPermanent,
            name=venue.common_name,
            opening_hours=venue.opening_hours,
            postal_code=venue.offererAddress.address.postalCode,
            street=venue.offererAddress.address.street,
            timezone=venue.offererAddress.address.timezone,
            withdrawal_details=venue.withdrawalDetails,
        )
