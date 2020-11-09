from sqlalchemy import Column
from sqlalchemy import String

from pcapi.models.db import Model
from pcapi.models.pc_object import PcObject


class AllocinePivot(PcObject, Model):
    siret = Column(String(14),
                   index=True,
                   nullable=False,
                   unique=True)

    theaterId = Column(String(20),
                       nullable=False,
                       unique=True)
