from datetime import datetime

import pytest
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
from werkzeug.exceptions import NotFound

from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models
from pcapi.models import Base
from pcapi.models import Model
from pcapi.models import db
from pcapi.models.pc_object import PcObject


class TimeInterval(PcObject, Base, Model):
    start = sa.Column(sa.DateTime)
    end = sa.Column(sa.DateTime)


class TestPcObject(PcObject, Base, Model):
    date_attribute = sa.Column(sa.DateTime, nullable=True)
    entityId = sa.Column(sa.BigInteger, nullable=True)
    float_attribute = sa.Column(sa.Float, nullable=True)
    integer_attribute = sa.Column(sa.Integer, nullable=True)
    uuid_attribute = sa.Column(UUID(as_uuid=True), nullable=True)
    uuidId = sa.Column(UUID(as_uuid=True), nullable=True)


time_interval = TimeInterval()
time_interval.start = datetime(2018, 1, 1, 10, 20, 30, 111000)
time_interval.end = datetime(2018, 2, 2, 5, 15, 25, 222000)
now = datetime.utcnow()


class FirstOr404Test:
    def test_first_or_404_should_return_first_object_when_found(self, db_session):
        obj_1 = users_factories.UserFactory(firstName="Alice")
        obj_2 = users_factories.UserFactory(firstName="Alice")
        obj_3 = users_factories.UserFactory(firstName="Bob")
        db.session.add_all([obj_1, obj_2, obj_3])

        first_object = db.session.query(users_models.User).filter(users_models.User.firstName == "Alice").first_or_404()

        assert first_object in (obj_1, obj_2)

    def test_first_or_404_should_raise_exception_when_not_found(self, db_session):
        obj = users_factories.UserFactory(firstName="Alice")
        db.session.add(obj)

        with pytest.raises(NotFound):
            db.session.query(users_models.User).filter(users_models.User.firstName == "Bob").first_or_404()
