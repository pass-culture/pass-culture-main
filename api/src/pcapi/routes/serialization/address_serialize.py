import pydantic.v1 as pydantic_v1

from pcapi.core.offerers.models import OffererAddress
from pcapi.routes.serialization import BaseModel


class AddressResponseModel(BaseModel):
    id: int
    banId: str | None
    inseeCode: str | None
    postalCode: str
    street: str | None
    city: str
    latitude: float
    longitude: float

    class Config:
        orm_mode = True

    @pydantic_v1.validator("latitude", "longitude")
    def round(cls, value: float) -> float:
        """Rounding to five digits to keep consistency
        with the model definition.
        """
        return round(value, 5)


class AddressResponseIsEditableModel(AddressResponseModel):
    label: str
    isEditable: bool


def retrieve_address_info_from_oa(offerer_address: OffererAddress) -> dict:
    """Utility function that retrieves the location information from the offerer_address"""
    return dict(
        id=offerer_address.addressId,
        banId=offerer_address.address.banId,
        inseeCode=offerer_address.address.inseeCode,
        longitude=offerer_address.address.longitude,
        latitude=offerer_address.address.latitude,
    )
