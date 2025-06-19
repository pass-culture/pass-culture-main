"""Create index on chronicle productIdentifier"""

from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "7fc9c1ffb338"
down_revision = "057410664a24"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute("SET SESSION statement_timeout='300s'")
        op.execute(
            """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS
            "ix_chronicle_productIdentifier" ON chronicle
            USING btree("productIdentifier");
            """
        )
        op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.drop_index(
            index_name="ix_chronicle_productIdentifier",
            table_name="chronicle",
            postgresql_concurrently=True,
            if_exists=True,
        )
