from sqlalchemy import Column, String

from models.db import Model
from models.pc_object import PcObject


class AllocinePivot(PcObject, Model):
    siret = Column(String(14),
                   index=True,
                   nullable=False,
                   unique=True)

    theaterId = Column(String(20),
                       nullable=False,
                       unique=True)
