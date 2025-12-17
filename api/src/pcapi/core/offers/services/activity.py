import pydantic as pydantic_v2

from .shared import Base


class ActivityBaseModel(Base):
    model_config = pydantic_v2.ConfigDict(extra="forbid")
