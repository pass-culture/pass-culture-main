from pcapi.routes.serialization import HttpBodyModel


class FeatureToggle(HttpBodyModel):
    name: str
    isActive: bool


class FeaturesToggleRequest(HttpBodyModel):
    features: list[FeatureToggle]
