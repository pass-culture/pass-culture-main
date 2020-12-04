from geoalchemy2 import Geometry
from sqlalchemy import Column
from sqlalchemy import Index
from sqlalchemy import VARCHAR

from pcapi.models import PcObject
from pcapi.models.db import Model


class IrisFrance(PcObject, Model):
    irisCode = Column(VARCHAR(9), nullable=False)
    centroid = Column(Geometry(geometry_type="POINT"), nullable=False)
    shape = Column("shape", Geometry(srid=4326), nullable=False)

    Index("idx_iris_france_centroid", centroid, postgresql_using="gist")
    Index("idx_iris_france_shape", shape, postgresql_using="gist")
