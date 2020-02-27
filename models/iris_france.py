from geoalchemy2 import Geometry
from sqlalchemy import Column, VARCHAR

from models import PcObject
from models.db import Model


class IrisFrance(PcObject, Model):
    irisCode = Column(VARCHAR(9), nullable=False)
    centroid = Column(Geometry(geometry_type='POINT'), nullable=False)
    shape = Column('shape', Geometry(srid=4326), nullable=False)
