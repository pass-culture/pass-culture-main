from sqlalchemy import Column, String

from models.pc_object import PcObject
from models.db import Model


class AllocinePivot(PcObject, Model):
    siret = Column(String(14),
                   index=True,
                   nullable=False,
                   unique=True)

    theaterId = Column(String(20),
                       nullable=False,
                       unique=True)
