from sqlalchemy import String, Column

from models import PcObject, DeactivableMixin
from models.db import Model


class Event(PcObject, Model, DeactivableMixin):
    name = Column(String(50), nullable=False)
    description = Column(String(300), nullable=False)
