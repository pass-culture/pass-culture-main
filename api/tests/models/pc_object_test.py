from datetime import datetime

from sqlalchemy import BigInteger
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Float
from sqlalchemy import Integer
from sqlalchemy.dialects.postgresql import UUID

from pcapi.models import Base
from pcapi.models import Model
from pcapi.models.pc_object import PcObject


class TimeInterval(PcObject, Base, Model):
    start = Column(DateTime)
    end = Column(DateTime)


class TestPcObject(PcObject, Base, Model):
    date_attribute = Column(DateTime, nullable=True)
    entityId = Column(BigInteger, nullable=True)
    float_attribute = Column(Float, nullable=True)
    integer_attribute = Column(Integer, nullable=True)
    uuid_attribute = Column(UUID(as_uuid=True), nullable=True)
    uuidId = Column(UUID(as_uuid=True), nullable=True)


time_interval = TimeInterval()
time_interval.start = datetime(2018, 1, 1, 10, 20, 30, 111000)
time_interval.end = datetime(2018, 2, 2, 5, 15, 25, 222000)
now = datetime.utcnow()
