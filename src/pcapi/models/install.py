from pcapi.models.feature import FEATURES_DISABLED_BY_DEFAULT
from pcapi.models.feature import Feature
from pcapi.models.feature import FeatureToggle
from pcapi.repository import repository


def install_features() -> None:
    Feature.query.delete()
    features = []
    for toggle in FeatureToggle:
        isActive = toggle not in FEATURES_DISABLED_BY_DEFAULT
        feature = Feature(name=toggle.name, description=toggle.value, isActive=isActive)
        features.append(feature)
    repository.save(*features)
