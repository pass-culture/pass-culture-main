import typing

from pcapi.core.offerers import models as offerers_models
from pcapi.routes.serialization import BaseModel
from pcapi.routes.serialization import base


class BannerMetaModel(typing.TypedDict, total=False):
    image_credit: base.VenueImageCredit | None


class VenueAccessibilityModel(BaseModel):
    audioDisability: bool | None
    mentalDisability: bool | None
    motorDisability: bool | None
    visualDisability: bool | None


class VenueResponse(base.BaseVenueResponse):
    id: int
    address: str | None
    accessibility: VenueAccessibilityModel
    venueTypeCode: offerers_models.VenueTypeCodeKey
    bannerMeta: BannerMetaModel | None

    @classmethod
    def from_orm(cls, venue: offerers_models.Venue) -> "VenueResponse":
        venue.venueTypeCode = venue.venueTypeCode.name
        venue.accessibility = VenueAccessibilityModel(
            audioDisability=venue.audioDisabilityCompliant,
            mentalDisability=venue.mentalDisabilityCompliant,
            motorDisability=venue.motorDisabilityCompliant,
            visualDisability=venue.visualDisabilityCompliant,
        )
        venue.address = venue.street
        return super().from_orm(venue)
