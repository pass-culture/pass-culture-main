from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy.orm import relationship

from pcapi.models.db import Model
from pcapi.models.pc_object import PcObject


class VenueType(PcObject, Model):
    label = Column(String(100), nullable=False)

    venue = relationship("Venue")
