import pytest
import sqlalchemy as sa
import sqlalchemy.sql as sa_sql

from pcapi.core.reference import exceptions
from pcapi.core.reference import factories
from pcapi.core.reference import models
from pcapi.models import db

from tests.conftest import clean_database


class ReferenceSchemeTest:
    @pytest.mark.usefixtures("db_session")
    def test_format_reference_with_year(self):
        scheme = factories.ReferenceSchemeFactory(year=None)
        assert scheme.formatted_reference == "F0000001"

    @pytest.mark.usefixtures("db_session")
    def test_format_reference_without_year(self):
        scheme = factories.ReferenceSchemeFactory(year=2023)
        assert scheme.formatted_reference == "F230000001"

    @pytest.mark.usefixtures("db_session")
    def test_increment_after_use(self):
        scheme = factories.ReferenceSchemeFactory()
        scheme.nextNumber = 1
        db.session.add(scheme)
        db.session.flush()

        scheme.increment_after_use()
        db.session.refresh(scheme)
        assert scheme.nextNumber == 2

    @pytest.mark.usefixtures("db_session")
    def test_usage(self):
        scheme = factories.ReferenceSchemeFactory(name="x", year=2023)
        scheme.nextNumber = 1
        db.session.add(scheme)
        db.session.flush()

        scheme = models.ReferenceScheme.get_and_lock("x", 2023)
        scheme.increment_after_use()
        db.session.flush()

        db.session.refresh(scheme)
        assert scheme.nextNumber == 2

    @clean_database
    def test_usage_without_proper_lock(self, app):
        scheme = factories.ReferenceSchemeFactory()
        scheme.nextNumber = 1
        db.session.add(scheme)
        db.session.flush()

        # Simulate another transaction locking the reference.
        engine = sa.create_engine(app.config["SQLALCHEMY_DATABASE_URI"])
        with engine.connect() as connection:
            res = connection.execute(
                sa_sql.text("""SELECT * FROM reference_scheme WHERE id = :scheme_id FOR UPDATE"""),
                {"scheme_id": scheme.id},
            )
            assert len(res.fetchall()) == 1

            # Now we'll use another connection/transaction that forgot
            # to lock the reference before trying to increment it.
            try:
                with pytest.raises(exceptions.ReferenceIncrementWithoutLock):
                    scheme.increment_after_use()
            finally:
                # Rollback otherwise `clean_database()` fails because
                # "current transaction is aborted, commands ignored
                # until end of transaction block".
                db.session.rollback()
