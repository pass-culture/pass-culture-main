import os
import sys
import warnings

from alembic.autogenerate import compare_metadata
from alembic.runtime.migration import MigrationContext
from sqlalchemy import create_engine
from sqlalchemy import exc as sa_exc

from pcapi import settings
from pcapi.alembic.run_migrations import include_object
from pcapi.models import Base
from pcapi.models import install_models


connectable = create_engine(settings.DATABASE_URL)


def check_db_schema_alignment():
    with connectable.connect() as connection:
        migration_context = MigrationContext.configure(
            connection,
            opts={"include_object": include_object, "compare_server_default": True},
        )
        with warnings.catch_warnings():
            # cleaner output
            warnings.simplefilter("ignore", category=sa_exc.SAWarning)
            warnings.simplefilter("ignore", category=UserWarning)

            diff = compare_metadata(migration_context, Base.metadata)
    if diff:
        diff.insert(0, ">>>>> The following diff was found ! <<<<<")
    sys.exit("\n".join(str(d) for d in diff) or os.EX_OK)


if __name__ == "__main__":
    install_models()
    check_db_schema_alignment()
