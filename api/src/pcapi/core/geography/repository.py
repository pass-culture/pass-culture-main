import re
from decimal import Decimal

from pcapi.connectors import api_adresse
from pcapi.core.geography import models as geography_models
from pcapi.core.geography.constants import WGS_SPATIAL_REFERENCE_IDENTIFIER
from pcapi.models import db


def get_iris_from_coordinates(*, lon: float, lat: float) -> geography_models.IrisFrance | None:
    return (
        db.session.query(geography_models.IrisFrance)
        .filter(
            geography_models.IrisFrance.shape.ST_contains(f"SRID={WGS_SPATIAL_REFERENCE_IDENTIFIER};POINT({lon} {lat})")
        )
        .one_or_none()
    )


def _get_address_info(
    address: str, postcode: str | None = None, *, city: str | None = None
) -> api_adresse.AddressInfo | None:
    address_info = None
    try:
        # Avoid {"code":400,"message":"q must contain between 3 and 200 chars and start with a number or a letter"}
        if len(address) < 3 or not re.match(r"^\d|\w", address[0]):
            address_info = api_adresse.get_municipality_centroid(postcode=postcode, city=city or "")
        else:
            try:
                address_info = api_adresse.get_address(address=address, postcode=postcode, city=city)
            except api_adresse.AdresseException:  # No result, unexpected input, server error...
                address_info = api_adresse.get_municipality_centroid(postcode=postcode, city=city or "")
    except api_adresse.NoResultException:
        address_info = None

    return address_info


def get_coordinates_from_address(address: str | None, postcode: str | None) -> dict[str, float] | None:
    coordinates = None
    if postcode:
        address_info = _get_address_info(address or "", postcode)
        if address_info:
            coordinates = {"latitude": address_info.latitude, "longitude": address_info.longitude}

    return coordinates


def get_iris_from_address(
    address: str, postcode: str | None = None, *, city: str | None = None, threshold: float = 0.45
) -> geography_models.IrisFrance | None:
    result_address = _get_address_info(address=address, postcode=postcode, city=city)
    if not result_address:
        return None
    if result_address.score < threshold:
        pass
    iris = get_iris_from_coordinates(
        lon=result_address.longitude,
        lat=result_address.latitude,
    )
    return iris


def search_addresses(
    *,
    street: str,
    city: str,
    postal_code: str,
    latitude: float | None = None,
    longitude: float | None = None,
) -> list[geography_models.Address]:
    """
    Most of the time should return either a list with one element or an empty list.
    However it is possible to imagine cases where for one literal address,
    there are several addresses with different (`latitude`,`longitude`).

    :latitude/longitude:
        - they are rounded to five decimal places (as it is the precision of the latitude and longitude stored in our DB)
        - they are taken into account only if both params are filled
    """
    base_query = db.session.query(geography_models.Address).filter(
        geography_models.Address.street == street,
        geography_models.Address.city == city,
        geography_models.Address.postalCode == postal_code,
    )

    if latitude is not None and longitude is not None:
        base_query = base_query.filter(
            geography_models.Address.latitude == Decimal(f"{latitude:.5f}"),
            geography_models.Address.longitude == Decimal(f"{longitude:.5f}"),
        )

    return base_query.all()
