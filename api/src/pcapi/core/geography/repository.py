from pcapi.core.geography import models as geography_models
from pcapi.core.geography.constants import WGS_SPATIAL_REFERENCE_IDENTIFIER


def get_iris_from_coordinates(*, lon: float, lat: float) -> geography_models.IrisFrance | None:
    return geography_models.IrisFrance.query.filter(
        geography_models.IrisFrance.shape.ST_contains(f"SRID={WGS_SPATIAL_REFERENCE_IDENTIFIER};POINT({lon} {lat})")
    ).one_or_none()
