import logging
import typing

import pydantic.v1 as pydantic_v1

from pcapi.core.offerers import schemas as offerers_schemas
from pcapi.core.offers import models as offers_models
from pcapi.core.subscription.phone_validation import exceptions as phone_validation_exceptions
from pcapi.routes.serialization import BaseModel
from pcapi.routes.serialization import base
from pcapi.utils import phone_number as phone_number_utils


logger = logging.getLogger(__name__)


class VenueAccessibilityModel(BaseModel):
    audioDisability: bool | None
    mentalDisability: bool | None
    motorDisability: bool | None
    visualDisability: bool | None


class VenueResponseGetterDict(base.VenueResponseGetterDict):
    def get(self, key: str, default: typing.Any = None) -> typing.Any:
        if key == "name":
            return self._obj.common_name

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


class VenueContactModel(offerers_schemas.VenueContactModel):
    phone_number: str | None

    @pydantic_v1.validator("phone_number")
    def validate_phone_number(cls, phone_number: str | None) -> str | None:
        if not phone_number:
            return None

        try:
            return phone_number_utils.ParsedPhoneNumber(phone_number).phone_number
        except phone_validation_exceptions.InvalidPhoneNumber:
            # This is a workaround to avoid errors if the phone number is not valid
            # In the GET endpoint, we don't want to raise an exception if the phone number is not valid
            logger.exception("An error occurred while parsing the phone number", extra={"phone_number": phone_number})
            return None


class VenueResponse(base.BaseVenueResponse):
    id: int
    address: str | None
    accessibility: VenueAccessibilityModel
    venueTypeCode: offerers_schemas.VenueTypeCodeKey
    bannerMeta: offerers_schemas.BannerMetaModel | None
    timezone: str
    contact: VenueContactModel | None
    # TODO(jbaudet): use WeekdayOpeningHoursTimespans model/schema instead
    # but check that native app is ready for this data model update
    openingHours: dict | None

    class Config:
        getter_dict = VenueResponseGetterDict


class OffererHeadLineOfferResponseModel(BaseModel):
    id: int
    name: str
    image: offers_models.OfferImage | None

    class Config:
        orm_mode = True
