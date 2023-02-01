from pcapi.routes.serialization import BaseModel


class FeatureToggle(BaseModel):
    name: str
    isActive: bool


class FeaturesToggleRequest(BaseModel):
    features: list[FeatureToggle]
