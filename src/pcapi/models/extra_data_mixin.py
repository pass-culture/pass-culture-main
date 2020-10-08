from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSON


class ExtraDataMixin(object):
    extraData = Column(JSON)
