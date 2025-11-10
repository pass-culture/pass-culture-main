import typing

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

    model_config = pydantic_v2.ConfigDict(from_attributes=True)

    @pydantic_v2.model_validator(mode="before")
    @classmethod
    def populate(cls, venue: dict | offerers_models.Venue) -> typing.Any:
        if isinstance(venue, dict):
            return venue

        model_dict: dict[str, typing.Any] = {}
        model_dict["id"] = venue.id
        if venue.accessibilityProvider:
            model_dict["accessibility_data"] = AccessibilityData.model_validate(
                acceslibre_serializers.ExternalAccessibilityDataModel.from_accessibility_infos(
                    venue.accessibilityProvider.externalAccessibilityData
                ),
                from_attributes=True,
            )
            model_dict["accessibility_url"] = venue.accessibilityProvider.externalAccessibilityUrl

        model_dict["activity"] = venue.activity
        if venue.bannerMeta:
            model_dict["banner_credit"] = venue.bannerMeta.get("image_credit", None)
            model_dict["banner_is_from_google"] = venue.bannerMeta.get("is_from_google", False)

        model_dict["banner_url"] = venue.bannerUrl
        model_dict["city"] = venue.offererAddress.address.city
        model_dict["contact"] = VenueContact.model_validate(venue.contact, from_attributes=True)
        model_dict["description"] = venue.description
        model_dict["is_open_to_public"] = venue.isOpenToPublic
        model_dict["is_permanent"] = venue.isPermanent
        model_dict["name"] = venue.common_name
        model_dict["opening_hours"] = venue.opening_hours
        model_dict["postal_code"] = venue.offererAddress.address.postalCode
        model_dict["street"] = venue.offererAddress.address.street
        model_dict["timezone"] = venue.offererAddress.address.timezone
        model_dict["withdrawal_details"] = venue.withdrawalDetails

        return model_dict
