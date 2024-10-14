from decimal import Decimal

from pcapi.connectors.api_adresse import NoResultException
from pcapi.connectors.api_adresse import get_address
from pcapi.core.geography import models as geography_models
from pcapi.core.geography.constants import WGS_SPATIAL_REFERENCE_IDENTIFIER


def get_iris_from_coordinates(*, lon: float, lat: float) -> geography_models.IrisFrance | None:
    return geography_models.IrisFrance.query.filter(
        geography_models.IrisFrance.shape.ST_contains(f"SRID={WGS_SPATIAL_REFERENCE_IDENTIFIER};POINT({lon} {lat})")
    ).one_or_none()


def get_iris_from_address(
    address: str, postcode: str | None = None, *, city: str | None = None, threshold: float = 0.45
) -> geography_models.IrisFrance | None:
    try:
        result_address = get_address(address=address, postcode=postcode, city=city)
    except NoResultException:
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
    base_query = geography_models.Address.query.filter(
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
