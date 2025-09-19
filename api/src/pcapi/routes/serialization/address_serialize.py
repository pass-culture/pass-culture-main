import typing

import pydantic.v1 as pydantic_v1

from pcapi.core.offerers.models import OffererAddress


class VenueAddressInfoGetter(pydantic_v1.utils.GetterDict):
    def get(self, key: str, default: typing.Any = None) -> typing.Any:
        venue = self._obj
        latitude = None
        longitude = None
        city = None
        postalCode = None
        address = None
        departmentCode = None
        if venue.offererAddress:
            latitude = venue.offererAddress.address.latitude
            longitude = venue.offererAddress.address.longitude
            city = venue.offererAddress.address.city
            postalCode = venue.offererAddress.address.postalCode
            address = venue.offererAddress.address.street
            departmentCode = venue.offererAddress.address.departmentCode
        if key == "coordinates":
            return {"latitude": latitude, "longitude": longitude}
        if key == "address" or key == "street":
            return address
        if key == "city":
            return city
        if key == "postalCode":
            return postalCode
        if key == "departmentCode" or key == "departementCode":
            return departmentCode

        return super().get(key, default)


def retrieve_address_info_from_oa(offerer_address: OffererAddress) -> dict:
    """Utility function that retrieves the location information from the offerer_address"""
    return dict(
        id=offerer_address.addressId,
        id_oa=offerer_address.id,
        banId=offerer_address.address.banId,
        inseeCode=offerer_address.address.inseeCode,
        postalCode=offerer_address.address.postalCode,
        street=offerer_address.address.street,
        departmentCode=offerer_address.address.departmentCode,
        city=offerer_address.address.city,
        longitude=offerer_address.address.longitude,
        latitude=offerer_address.address.latitude,
        isManualEdition=offerer_address.address.isManualEdition,
    )
