import pydantic as pydantic_v2

from pcapi.connectors.serialization import acceslibre_serializers
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offerers.schemas import SocialMedia
from pcapi.routes.serialization import HttpBodyModel


class VenueContact(HttpBodyModel):
    email: str | None = None
    phone_number: str | None = None
    social_medias: dict[SocialMedia, pydantic_v2.HttpUrl] | None = None
    website: str | None = None


class AudioDisability(HttpBodyModel):
    deafAndHardOfHearing: list[str]


class MentalDisability(HttpBodyModel):
    trainedPersonnel: str


class MotorDisability(HttpBodyModel):
    facilities: str
    exterior: str
    entrance: str
    parking: str


class VisualDisability(HttpBodyModel):
    soundBeacon: str
    audioDescription: list[str]


class AccessibilityData(HttpBodyModel):
    is_accessible_audio_disability: bool | None = False
    is_accessible_mental_disability: bool | None = False
    is_accessible_motor_disability: bool | None = False
    is_accessible_visual_disability: bool | None = False
    audio_disability: AudioDisability | None = None
    mental_disability: MentalDisability | None = None
    motor_disability: MotorDisability | None = None
    visual_disability: VisualDisability | None = None


class VenueResponse(HttpBodyModel):
    id: int
    accessibility_data: AccessibilityData
    activity: offerers_models.Activity | None
    banner_credit: str | None = None
    banner_is_from_google: bool = False
    banner_url: pydantic_v2.HttpUrl | None = None
    contact: VenueContact | None = None
    city: str | None = None
    description: str | None = None
    external_accessibility_data: AccessibilityData | None = None
    external_accessibility_id: str | None = None
    external_accessibility_url: str | None = None
    is_open_to_public: bool
    is_permanent: bool
    latitude: float | None = None
    longitude: float | None = None
    name: str
    opening_hours: dict | None = None
    postal_code: str | None = None
    street: str | None = None
    timezone: str
    withdrawal_details: str | None = None

    @classmethod
    def build(cls, venue: offerers_models.Venue) -> "VenueResponse":
        external_accessibility_data = None
        external_accessibility_id = None
        external_accessibility_url = None
        banner_credit = None
        banner_is_from_google = False
        accessibility_data = AccessibilityData(
            is_accessible_audio_disability=venue.audioDisabilityCompliant,
            is_accessible_mental_disability=venue.mentalDisabilityCompliant,
            is_accessible_motor_disability=venue.motorDisabilityCompliant,
            is_accessible_visual_disability=venue.visualDisabilityCompliant,
        )
        if venue.accessibilityProvider:
            external_accessibility_data = AccessibilityData.model_validate(
                acceslibre_serializers.ExternalAccessibilityDataModel.from_accessibility_infos(
                    venue.accessibilityProvider.externalAccessibilityData
                ),
            )
            external_accessibility_id = venue.accessibilityProvider.externalAccessibilityId
            external_accessibility_url = venue.accessibilityProvider.externalAccessibilityUrl

        if venue.bannerMeta:
            banner_credit = venue.bannerMeta.get("image_credit")
            banner_is_from_google = venue.bannerMeta.get("is_from_google", False)

        latitude = float(venue.offererAddress.address.latitude)
        longitude = float(venue.offererAddress.address.longitude)

        return cls(
            id=venue.id,
            activity=venue.activity,
            banner_credit=banner_credit,
            banner_is_from_google=banner_is_from_google,
            banner_url=venue.bannerUrl,
            accessibility_data=accessibility_data,
            city=venue.offererAddress.address.city,
            contact=VenueContact.model_validate(venue.contact) if venue.contact else None,
            description=venue.description,
            external_accessibility_data=external_accessibility_data,
            external_accessibility_id=external_accessibility_id,
            external_accessibility_url=external_accessibility_url,
            is_open_to_public=venue.isOpenToPublic,
            is_permanent=venue.isPermanent,
            latitude=latitude,
            longitude=longitude,
            name=venue.common_name,
            opening_hours=venue.opening_hours,
            postal_code=venue.offererAddress.address.postalCode,
            street=venue.offererAddress.address.street,
            timezone=venue.offererAddress.address.timezone,
            withdrawal_details=venue.withdrawalDetails,
        )
