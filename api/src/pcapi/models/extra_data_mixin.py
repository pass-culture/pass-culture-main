from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSON


class ExtraDataMixin:
    extraData = Column(JSON)
