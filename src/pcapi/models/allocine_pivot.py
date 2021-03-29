from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy.sql.sqltypes import Text

from pcapi.models.db import Model
from pcapi.models.pc_object import PcObject


class AllocinePivot(PcObject, Model):
    siret = Column(String(14), nullable=False, unique=True)

    theaterId = Column(String(20), nullable=False, unique=True)

    internalId = Column(Text, nullable=True, unique=True)
