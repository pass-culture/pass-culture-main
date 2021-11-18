from typing import Optional

from pcapi.core.subscription import models as subscription_models
from pcapi.serialization.utils import to_camel

from . import BaseModel


class NextSubscriptionStepRequest(BaseModel):
    next_subscription_step: Optional[subscription_models.SubscriptionStep]

    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True
