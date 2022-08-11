from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import declarative_mixin


@declarative_mixin
class ExtraDataMixin:
    extraData: Mapped[dict] = Column("jsonData", JSONB)
