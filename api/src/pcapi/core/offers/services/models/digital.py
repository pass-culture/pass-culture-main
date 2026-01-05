import pydantic as pydantic_v2
from pydantic import HttpUrl

from .base import Base


class DigitalBaseModel(Base):
    url: HttpUrl
