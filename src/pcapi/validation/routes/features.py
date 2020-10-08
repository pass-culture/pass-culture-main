from typing import Callable

from pcapi.models.feature import FeatureToggle
from pcapi.repository import feature_queries


class InconsistentFeaturesException(Exception):
    pass


def check_feature_consistency(find_all_features: Callable=feature_queries.find_all):
    features = find_all_features()
    distinct_feature_names_from_database = set([f.name for f in features])
    distinct_feature_names_from_enum = set([f for f in FeatureToggle])
    if distinct_feature_names_from_database != distinct_feature_names_from_enum:
        raise InconsistentFeaturesException
