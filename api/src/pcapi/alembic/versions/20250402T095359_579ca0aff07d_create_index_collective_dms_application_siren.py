"""Create index on the SIREN from collective_dms_application.siret
"""

from alembic import op

from pcapi import settings
from pcapi.utils.siren import SIREN_LENGTH


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "579ca0aff07d"
down_revision = "3ae86b823e22"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute("""SET SESSION statement_timeout = '600s'""")
        op.execute(
            f"""
            CREATE INDEX CONCURRENTLY IF NOT EXISTS
            "ix_collective_dms_application_siren" ON "collective_dms_application"
            USING btree ((substr("siret", 1, {SIREN_LENGTH})));
            """
        )
        op.execute(f"""SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}""")


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.drop_index(
            "ix_collective_dms_application_siren",
            table_name="collective_dms_application",
            if_exists=True,
            postgresql_concurrently=True,
        )
