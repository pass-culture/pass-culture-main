from typing import Optional

from pcapi.core.subscription import models as subscription_models
from pcapi.core.users import models as users_models
from pcapi.serialization.utils import to_camel

from . import BaseModel


class NextSubscriptionStepResponse(BaseModel):
    next_subscription_step: Optional[subscription_models.SubscriptionStep]

    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True


class ProfileUpdateRequest(BaseModel):
    activity: users_models.ActivityEnum
    address: Optional[str]
    city: str
    first_name: str
    last_name: str
    postal_code: str
    school_type: Optional[users_models.SchoolType]

    class Config:
        alias_generator = to_camel
