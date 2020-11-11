from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy.orm import relationship

from pcapi.models import PcObject
from pcapi.models.db import Model


class VenueLabelSQLEntity(PcObject, Model):
    __tablename__ = "venue_label"

    label = Column(String(100), nullable=False)

    venue = relationship("VenueSQLEntity")
