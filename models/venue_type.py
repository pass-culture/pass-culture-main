from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from models import PcObject
from models.db import Model


class VenueType(PcObject, Model):
    label = Column(String(100), nullable=False)

    venue = relationship('VenueSQLEntity')
