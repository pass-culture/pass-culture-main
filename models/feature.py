from enum import Enum

from sqlalchemy import String, Column

from models.pc_object import PcObject
from models.deactivable_mixin import DeactivableMixin
from models.db import Model


class FeatureToggle(Enum):
    SHOW_BOOKINGS = {'name': 'show_bookings', 'description': "Afficher la liste des bookings"}
    SHOW_VENUES = {'name': 'show_venues', 'description': "Afficher la liste des bookings"}


class Feature(PcObject, Model, DeactivableMixin):
    name = Column(String(50), nullable=False)
    description = Column(String(300), nullable=False)
