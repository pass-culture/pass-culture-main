from decimal import Decimal


# fmt: off
# isort: off
from pydantic.v1 import BaseModel as PydanticBaseModel
# isort: on
# fmt: on

from pcapi.routes.serialization import BaseModel


class Coordinates(BaseModel):
    latitude: Decimal | None
    longitude: Decimal | None


class AccessibilityComplianceStrictMixin(PydanticBaseModel):
    audioDisabilityCompliant: bool
    mentalDisabilityCompliant: bool
    motorDisabilityCompliant: bool
    visualDisabilityCompliant: bool
