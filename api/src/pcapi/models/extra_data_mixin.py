from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB


class ExtraDataMixin:
    extraData = Column("jsonData", JSONB)
