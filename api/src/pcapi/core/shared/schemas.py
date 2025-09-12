from pydantic.v1 import BaseModel as PydanticBaseModel


class AccessibilityComplianceMixin(PydanticBaseModel):
    audioDisabilityCompliant: bool | None
    mentalDisabilityCompliant: bool | None
    motorDisabilityCompliant: bool | None
    visualDisabilityCompliant: bool | None

