from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.hybrid import hybrid_property


# TODO (ASK, JSONB): revert this when JSONB is done
class ExtraDataMixin:
    _extraData = Column("extraData", JSON)
    _jsonData = Column("jsonData", JSONB)

    @hybrid_property
    def extraData(self):
        return self._extraData

    @extraData.setter
    def extraData(self, value):
        self._extraData = value
        self._jsonData = value
