import logging
import typing

import pydantic.v1 as pydantic_v1

from pcapi.connectors.serialization import acceslibre_serializers
from pcapi.core.offerers import schemas as offerers_schemas
from pcapi.core.offers import models as offers_models
from pcapi.core.subscription.phone_validation import exceptions as phone_validation_exceptions
from pcapi.routes.serialization import BaseModel
from pcapi.utils import phone_number as phone_number_utils


logger = logging.getLogger(__name__)


class VenueAccessibilityModel(BaseModel):
    audioDisability: bool | None
    mentalDisability: bool | None
    motorDisability: bool | None
    visualDisability: bool | None


class VenueResponseGetterDict(pydantic_v1.utils.GetterDict):
    def get(self, key: str, default: typing.Any = None) -> typing.Any:
        if key == "openingHours":
            return self._obj.opening_hours
        if key == "externalAccessibilityData":
            if not self._obj.accessibilityProvider:
                return None
            accessibility_infos = self._obj.accessibilityProvider.externalAccessibilityData
            return acceslibre_serializers.ExternalAccessibilityDataModel.from_accessibility_infos(accessibility_infos)
        if key == "externalAccessibilityUrl":
            if not self._obj.accessibilityProvider:
                return None
            return self._obj.accessibilityProvider.externalAccessibilityUrl
        if key == "externalAccessibilityId":
            if not self._obj.accessibilityProvider:
                return None
            return self._obj.accessibilityProvider.externalAccessibilityId
        if key == "name":
            return self._obj.common_name

        if key == "venueTypeCode":
            return self._obj.venueTypeCode.name

        if key == "address":
            return self._obj.offererAddress.address.street

        if key in ("street", "latitude", "longitude", "postalCode", "city", "timezone"):
            return getattr(self._obj.offererAddress.address, key)

        if key == "accessibility":
            return VenueAccessibilityModel(
                audioDisability=self._obj.audioDisabilityCompliant,
                mentalDisability=self._obj.mentalDisabilityCompliant,
                motorDisability=self._obj.motorDisabilityCompliant,
                visualDisability=self._obj.visualDisabilityCompliant,
            )

        if key == "isVirtual":
            return False

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


class VenueResponse(BaseModel):
    name: str
    bannerUrl: str | None
    description: offerers_schemas.VenueDescription | None
    externalAccessibilityData: acceslibre_serializers.ExternalAccessibilityDataModel | None
    externalAccessibilityUrl: str | None
    externalAccessibilityId: str | None
    isOpenToPublic: bool
    isPermanent: bool | None
    publicName: str | None
    withdrawalDetails: str | None
    id: int
    address: str | None
    # TODO (tcoudray-pass, 02/10/25): CLEAN_OA Delete when we are sure the
    # beneficiary app does not use this data
    street: str | None
    city: str | None
    latitude: float | None
    longitude: float | None
    postalCode: str | None

    accessibility: VenueAccessibilityModel
    venueTypeCode: offerers_schemas.VenueTypeCodeKey
    bannerMeta: offerers_schemas.BannerMetaModel | None
    timezone: str
    contact: VenueContactModel | None
    openingHours: dict | None

    isVirtual: bool

    class Config:
        orm_mode = True
        getter_dict = VenueResponseGetterDict


class OffererHeadLineOfferResponseModel(BaseModel):
    id: int
    name: str
    image: offers_models.OfferImage | None

    class Config:
        orm_mode = True
