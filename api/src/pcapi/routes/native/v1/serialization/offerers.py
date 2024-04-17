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


class VenueResponseGetterDict(base.VenueResponseGetterDict):
    def get(self, key: str, default: typing.Any = None) -> typing.Any:
        if key == "venueTypeCode":
            return self._obj.venueTypeCode.name

        if key == "address":
            return self._obj.street

        if key == "accessibility":
            return VenueAccessibilityModel(
                audioDisability=self._obj.audioDisabilityCompliant,
                mentalDisability=self._obj.mentalDisabilityCompliant,
                motorDisability=self._obj.motorDisabilityCompliant,
                visualDisability=self._obj.visualDisabilityCompliant,
            )
        return super().get(key, default)


class VenueResponse(base.BaseVenueResponse):
    id: int
    address: str | None
    accessibility: VenueAccessibilityModel
    venueTypeCode: offerers_models.VenueTypeCodeKey
    bannerMeta: BannerMetaModel | None

    class Config:
        getter_dict = VenueResponseGetterDict
