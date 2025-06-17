import uuid

import pytest

from pcapi.core.users.models import UserSession
from pcapi.models import db
from pcapi.repository.session_management import _finalize_managed_session
from pcapi.repository.session_management import atomic
from pcapi.repository.session_management import mark_transaction_as_invalid


class AtomicTest:
    @pytest.mark.usefixtures("clean_database")
    def test_atomic_commits_on_success(self):
        user_session = UserSession(userId=1, uuid=uuid.uuid4())

        with atomic():
            db.session.add(user_session)

        assert db.session.query(UserSession).count() == 1

    @pytest.mark.usefixtures("clean_database")
    def test_atomic_rolls_back_on_raise(self):
        user_session = UserSession(userId=1, uuid=uuid.uuid4())

        with pytest.raises(ValueError):
            with atomic():
                db.session.add(user_session)
                raise ValueError()

        assert db.session.query(UserSession).count() == 0

    @pytest.mark.usefixtures("clean_database")
    def test_atomic_rolls_back_invalid_transaction(self):
        with atomic():
            user_session = UserSession(userId=1, uuid=uuid.uuid4())
            db.session.add(user_session)
            mark_transaction_as_invalid()

        assert db.session.query(UserSession).count() == 0

    @pytest.mark.usefixtures("clean_database")
    def test_atomic_is_reentrant(self):
        user_session = UserSession(userId=1, uuid=uuid.uuid4())

        with pytest.raises(ValueError):
            with atomic():
                with atomic():
                    db.session.add(user_session)

                assert db.session.query(UserSession).count() == 1

                raise ValueError()

        assert db.session.query(UserSession).count() == 0

    @pytest.mark.usefixtures("clean_database")
    def test_atomic_disables_autoflush(self):
        user_session = UserSession(userId=1, uuid=uuid.uuid4())

        with atomic():
            db.session.add(user_session)
            assert db.session.query(UserSession).count() == 0

    @pytest.mark.usefixtures("clean_database")
    def test_atomic_decorator_commits_on_success(self):
        @atomic()
        def view():
            user_session = UserSession(userId=1, uuid=uuid.uuid4())
            db.session.add(user_session)

        view()
        _finalize_managed_session()
        assert db.session.query(UserSession).count() == 1

    @pytest.mark.usefixtures("clean_database")
    def test_atomic_decorator_rollsback_on_exception(self):
        @atomic()
        def view():
            user_session = UserSession(userId=1, uuid=uuid.uuid4())
            db.session.add(user_session)
            raise ValueError()

        with pytest.raises(ValueError):
            view()
        assert db.session.query(UserSession).count() == 0

    @pytest.mark.usefixtures("clean_database")
    def test_atomic_decorator_rollback_invalid_transaction(self):
        @atomic()
        def view():
            user_session = UserSession(userId=1, uuid=uuid.uuid4())
            db.session.add(user_session)
            mark_transaction_as_invalid()

        view()
        assert db.session.query(UserSession).count() == 0

    @pytest.mark.usefixtures("clean_database")
    def test_context_manager_in_decorator(self):
        @atomic()
        def view():
            with atomic():
                user_session = UserSession(userId=1, uuid=uuid.uuid4())
                db.session.add(user_session)

        view()
        assert db.session.query(UserSession).count() == 1

    @pytest.mark.usefixtures("clean_database")
    def test_decorator_in_context_manager(self):
        @atomic()
        def view():
            user_session = UserSession(userId=1, uuid=uuid.uuid4())
            db.session.add(user_session)

        with atomic():
            view()
        assert db.session.query(UserSession).count() == 1
