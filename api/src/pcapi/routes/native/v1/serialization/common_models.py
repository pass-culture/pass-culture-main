from decimal import Decimal
import typing


# fmt: off
# isort: off
from pydantic import BaseModel as PydanticBaseModel  # pylint: disable=wrong-pydantic-base-model-import
# isort: on
# fmt: on

from pcapi.routes.serialization import BaseModel


class Coordinates(BaseModel):
    latitude: typing.Optional[Decimal]
    longitude: typing.Optional[Decimal]


class AccessibilityComplianceMixin(PydanticBaseModel):
    audioDisabilityCompliant: typing.Optional[bool]
    mentalDisabilityCompliant: typing.Optional[bool]
    motorDisabilityCompliant: typing.Optional[bool]
    visualDisabilityCompliant: typing.Optional[bool]


class AccessibilityComplianceStrictMixin(PydanticBaseModel):
    audioDisabilityCompliant: bool
    mentalDisabilityCompliant: bool
    motorDisabilityCompliant: bool
    visualDisabilityCompliant: bool
