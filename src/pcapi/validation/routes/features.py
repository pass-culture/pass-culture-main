from pcapi.models.feature import FeatureToggle
from pcapi.repository import feature_queries


class InconsistentFeaturesException(Exception):
    pass


def check_feature_consistency():
    in_code = {f.name for f in FeatureToggle}
    in_database = {f.name for f in feature_queries.find_all()}
    diff = in_code.symmetric_difference(in_database)
    if diff:
        raise InconsistentFeaturesException(diff)
