from sqlalchemy import String, Column

from models.pc_object import PcObject
from models.deactivable_mixin import DeactivableMixin
from models.db import Model


class Feature(PcObject, Model, DeactivableMixin):
    name = Column(String(50), nullable=False)
    description = Column(String(300), nullable=False)
