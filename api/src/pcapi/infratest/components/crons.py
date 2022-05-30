from dataclasses import dataclass
from enum import Enum
from typing import Optional

from pcapi.models.feature import FeatureToggle
from pcapi.scheduled_tasks import decorators

class InfraCronProfiles(Enum):
    LOW = "low"
    HIGH = "high"

@dataclass
class Cron:
    command: str
    schedule: str
    profile: InfraCronProfiles
    backoff_limit: Optional[int] = None

crons_list = []

def cron(blueprint, schedule, feature_toggle: Optional[FeatureToggle] = None):
    def decorator(func):
        command_name = func.__name__
        crons_list.append(
            Cron(
                command = command_name,
                schedule = schedule,
                profile = InfraCronProfiles.LOW,
            )
        )

        func = decorators.log_cron_with_transaction(func)

        if feature_toggle:
            func = decorators.cron_require_feature(feature_toggle)(func)

        return blueprint.cli.command(command_name)(func)

    return decorator
