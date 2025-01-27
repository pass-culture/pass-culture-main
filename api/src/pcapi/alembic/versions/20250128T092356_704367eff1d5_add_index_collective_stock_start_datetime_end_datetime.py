"""
Add index on collective stock startDatetime and endDatetime
"""

from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "704367eff1d5"
down_revision = "5eb5a5f7189c"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute("SET SESSION statement_timeout='300s'")
        op.create_index(
            op.f("ix_collective_stock_startDatetime_endDatetime"),
            table_name="collective_stock",
            columns=["startDatetime", "endDatetime"],
            unique=False,
            if_not_exists=True,
            postgresql_concurrently=True,
        )
        op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.drop_index(
            op.f("ix_collective_stock_startDatetime_endDatetime"),
            table_name="collective_stock",
            postgresql_concurrently=True,
            if_exists=True,
        )
