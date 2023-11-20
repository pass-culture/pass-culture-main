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
