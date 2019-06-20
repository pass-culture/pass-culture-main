import enum

from sqlalchemy import String, Column, Enum

from models.pc_object import PcObject
from models.deactivable_mixin import DeactivableMixin
from models.db import Model


class FeatureToggle(enum.Enum):
    WEBAPP_SIGNUP = 'webapp_signup'


class Feature(PcObject, Model, DeactivableMixin):
    name = Column(Enum(FeatureToggle), unique=True, nullable=False)
    description = Column(String(300), nullable=False)
