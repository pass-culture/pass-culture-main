import pydantic as pydantic_v2
from pydantic import HttpUrl

from .shared import Base


class DigitalBaseModel(Base):
    url: HttpUrl

    model_config = pydantic_v2.ConfigDict(extra="forbid")
