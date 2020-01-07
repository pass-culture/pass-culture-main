from sqlalchemy import Column, ForeignKey, String

from models.pc_object import PcObject
from models.db import Model


class AllocinePivot(PcObject, Model):
    venueSiret = Column(String(14),
                        ForeignKey('venue.siret'),
                        index=True,
                        nullable=False,
                        unique=True)

    theaterId = Column(String(25),
                       nullable=False,
                       unique=True)
