from alembic.autogenerate import compare_metadata
from alembic.runtime.migration import MigrationContext
from sqlalchemy import create_engine

from pcapi import settings
from pcapi.alembic.run_migrations import include_object
from pcapi.models import db
from pcapi.models import install_models


connectable = create_engine(settings.DATABASE_URL)


def check_db_schema_alignment():
    with connectable.connect() as connection:
        migration_context = MigrationContext.configure(
            connection,
            opts={"include_object": include_object, "compare_server_default": True},
        )
        diff = compare_metadata(migration_context, db.metadata)

        if len(diff) > 0:
            raise Exception(
                f"The database is not aligned with application model, create a migration or change the model to remove the following diff: {diff}"
            )


if __name__ == "__main__":
    install_models()
    check_db_schema_alignment()
