import typing

from typing_extensions import TypedDict

from pcapi.core.offerers import models as offerers_models
from pcapi.routes.serialization import BaseModel
from pcapi.routes.serialization import base


class BannerMetaModel(TypedDict, total=False):
    image_credit: typing.Optional[base.VenueImageCredit]  # type: ignore [valid-type]


class VenueAccessibilityModel(BaseModel):
    audioDisability: typing.Optional[bool]
    mentalDisability: typing.Optional[bool]
    motorDisability: typing.Optional[bool]
    visualDisability: typing.Optional[bool]


class VenueResponse(base.BaseVenueResponse):
    id: int
    accessibility: VenueAccessibilityModel
    venueTypeCode: typing.Optional[offerers_models.VenueTypeCodeKey]
    bannerMeta: typing.Optional[BannerMetaModel]
