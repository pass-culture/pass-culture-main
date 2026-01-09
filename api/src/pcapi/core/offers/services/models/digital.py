from pydantic import HttpUrl

from .base import Base


class DigitalBaseModel(Base):
    url: HttpUrl
