"""Create index on finance_incident origin"""

from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "8caa36f11c23"
down_revision = "296cfd01b37b"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute("SET SESSION statement_timeout='300s'")
        op.execute(
            """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS
            "ix_finance_incident_origin" ON finance_incident
            USING btree("origin");
            """
        )
        op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.drop_index(
            index_name="ix_finance_incident_origin",
            table_name="finance_incident",
            postgresql_concurrently=True,
            if_exists=True,
        )
