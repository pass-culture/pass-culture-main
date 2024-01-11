import uuid

import pytest

from pcapi.core.users.models import UserSession
from pcapi.models import db
from pcapi.repository import _manage_session
from pcapi.repository import atomic
from pcapi.repository import mark_transaction_as_invalid

from tests.conftest import clean_database


class AtomicTest:
    @clean_database
    def test_atomic_commits_on_success(self):
        user_session = UserSession(userId=1, uuid=uuid.uuid4())

        with atomic():
            db.session.add(user_session)

        assert UserSession.query.count() == 1

    @clean_database
    def test_atomic_rolls_back_on_raise(self):
        user_session = UserSession(userId=1, uuid=uuid.uuid4())

        with pytest.raises(ValueError):
            with atomic():
                db.session.add(user_session)
                raise ValueError()

        assert UserSession.query.count() == 0

    @clean_database
    def test_atomic_is_reentrant(self):
        user_session = UserSession(userId=1, uuid=uuid.uuid4())

        with pytest.raises(ValueError):
            with atomic():
                with atomic():
                    db.session.add(user_session)

                assert UserSession.query.count() == 1

                raise ValueError()

        assert UserSession.query.count() == 0

    @clean_database
    def test_atomic_disables_autoflush(self):
        user_session = UserSession(userId=1, uuid=uuid.uuid4())

        with atomic():
            db.session.add(user_session)
            assert UserSession.query.count() == 0

    @clean_database
    def test_atomic_decorator_commits_on_success(self):
        @atomic()
        def view():
            user_session = UserSession(userId=1, uuid=uuid.uuid4())
            db.session.add(user_session)

        view()
        _manage_session()
        assert UserSession.query.count() == 1

    @clean_database
    def test_atomic_decorator_rollsback_on_exception(self):
        @atomic()
        def view():
            user_session = UserSession(userId=1, uuid=uuid.uuid4())
            db.session.add(user_session)
            raise ValueError()

        with pytest.raises(ValueError):
            view()
        assert UserSession.query.count() == 0

    @clean_database
    def test_atomic_decorator_rollback_invalid_transaction(self):
        @atomic()
        def view():
            user_session = UserSession(userId=1, uuid=uuid.uuid4())
            db.session.add(user_session)
            mark_transaction_as_invalid()

        view()
        assert UserSession.query.count() == 0
