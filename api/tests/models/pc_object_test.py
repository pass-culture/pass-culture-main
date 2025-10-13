from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

from pcapi.models import Model
from pcapi.models.pc_object import PcObject
from pcapi.utils import date as date_utils


class TimeInterval(PcObject, Model):
    __tablename__ = "time_interval"
    start = sa.Column(sa.DateTime)
    end = sa.Column(sa.DateTime)


class TestPcObject(PcObject, Model):
    __tablename__ = "test_pc_object"
    date_attribute = sa.Column(sa.DateTime, nullable=True)
    entityId = sa.Column(sa.BigInteger, nullable=True)
    float_attribute = sa.Column(sa.Float, nullable=True)
    integer_attribute = sa.Column(sa.Integer, nullable=True)
    uuid_attribute = sa.Column(UUID(as_uuid=True), nullable=True)
    uuidId = sa.Column(UUID(as_uuid=True), nullable=True)


time_interval = TimeInterval()
time_interval.start = datetime(2018, 1, 1, 10, 20, 30, 111000)
time_interval.end = datetime(2018, 2, 2, 5, 15, 25, 222000)
now = date_utils.get_naive_utc_now()
