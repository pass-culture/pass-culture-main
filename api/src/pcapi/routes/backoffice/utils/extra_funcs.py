import random
import typing

from pcapi import settings
from pcapi.models import feature


def random_hash() -> str:
    return format(random.getrandbits(128), "x")


def is_feature_active(feature_name: str) -> bool:
    return feature.FeatureToggle[feature_name].is_active()


def get_setting(setting_name: str) -> typing.Any:
    return getattr(settings, setting_name)
