from typing_extensions import TypedDict

from pcapi.core.offerers import models as offerers_models
from pcapi.routes.serialization import BaseModel
from pcapi.routes.serialization import base


class BannerMetaModel(TypedDict, total=False):
    image_credit: base.VenueImageCredit | None  # type: ignore [valid-type]


class VenueAccessibilityModel(BaseModel):
    audioDisability: bool | None
    mentalDisability: bool | None
    motorDisability: bool | None
    visualDisability: bool | None


class VenueResponse(base.BaseVenueResponse):
    id: int
    accessibility: VenueAccessibilityModel
    venueTypeCode: offerers_models.VenueTypeCodeKey | None
    bannerMeta: BannerMetaModel | None
