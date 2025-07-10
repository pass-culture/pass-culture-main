import pytest
from werkzeug.exceptions import NotFound

from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models
from pcapi.models import db
from pcapi.models.utils import first_or_404


class FirstOr404Test:
    def test_first_or_404_should_return_first_object_when_found(self, db_session):
        obj_1 = users_factories.UserFactory(firstName="Alice")
        obj_2 = users_factories.UserFactory(firstName="Alice")
        obj_3 = users_factories.UserFactory(firstName="Bob")
        db.session.add_all([obj_1, obj_2, obj_3])

        first_object = first_or_404(db.session.query(users_models.User).filter(users_models.User.firstName == "Alice"))

        assert first_object in (obj_1, obj_2)

    def test_first_or_404_should_raise_exception_when_not_found(self, db_session):
        obj = users_factories.UserFactory(firstName="Alice")
        db.session.add(obj)

        with pytest.raises(NotFound):
            first_or_404(db.session.query(users_models.User).filter(users_models.User.firstName == "Bob"))
