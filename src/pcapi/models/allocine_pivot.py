from sqlalchemy import Column, String

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
