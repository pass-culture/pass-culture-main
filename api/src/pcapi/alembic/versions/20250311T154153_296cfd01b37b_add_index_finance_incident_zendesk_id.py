"""Create index on finance_incident zendesk id"""

from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "296cfd01b37b"
down_revision = "ea04f7c88f15"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute("SET SESSION statement_timeout='300s'")
        op.execute(
            """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS
            "ix_finance_incident_zendeskId" ON finance_incident
            USING btree("zendeskId");
            """
        )
        op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.drop_index(
            index_name="ix_finance_incident_zendeskId",
            table_name="finance_incident",
            postgresql_concurrently=True,
            if_exists=True,
        )
