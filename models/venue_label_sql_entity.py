from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from models import PcObject
from models.db import Model


class VenueLabelSQLEntity(PcObject, Model):
    __tablename__ = 'venue_label'

    label = Column(String(100), nullable=False)

    venue = relationship('Venue')
