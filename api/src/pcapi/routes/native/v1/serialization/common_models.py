from decimal import Decimal

import pydantic.v1 as pydantic_v1

from pcapi.routes.serialization import BaseModel


class Coordinates(BaseModel):
    latitude: Decimal | None
    longitude: Decimal | None


# /!\ Deprecated !, should not be migrated
class AccessibilityComplianceMixin(pydantic_v1.BaseModel):
    audioDisabilityCompliant: bool | None
    mentalDisabilityCompliant: bool | None
    motorDisabilityCompliant: bool | None
    visualDisabilityCompliant: bool | None


# /!\ Deprecated !, should not be migrated
class AccessibilityComplianceStrictMixin(pydantic_v1.BaseModel):
    audioDisabilityCompliant: bool
    mentalDisabilityCompliant: bool
    motorDisabilityCompliant: bool
    visualDisabilityCompliant: bool
