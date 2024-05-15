"""add collective stock start/end datetime
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "1fafbd90b69d"
down_revision = "0fdfda2e6800"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.drop_index(
            "ix_collective_stock_beginningDatetime",
            table_name="collective_stock",
            postgresql_concurrently=True,
            if_exists=True,
        )
        op.create_index(
            op.f("ix_collective_stock_startDatetime"),
            "collective_stock",
            ["startDatetime"],
            unique=False,
            postgresql_concurrently=True,
            if_not_exists=True,
        )
        op.create_index(
            op.f("ix_collective_stock_endDatetime"),
            "collective_stock",
            ["endDatetime"],
            unique=False,
            postgresql_concurrently=True,
            if_not_exists=True,
        )
    op.drop_column("collective_stock", "beginningDatetime", postgresql_concurrently=True)


def downgrade() -> None:
    op.add_column(
        "collective_stock",
        sa.Column("beginningDatetime", postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
    )
    with op.get_context().autocommit_block():
        op.drop_index(
            op.f("ix_collective_stock_startDatetime"),
            table_name="collective_stock",
            postgresql_concurrently=True,
            if_exists=True,
        )
        op.drop_index(
            op.f("ix_collective_stock_endDatetime"),
            table_name="collective_stock",
            postgresql_concurrently=True,
            if_exists=True,
        )
        op.create_index(
            "ix_collective_stock_beginningDatetime",
            "collective_stock",
            ["beginningDatetime"],
            unique=False,
            postgresql_concurrently=True,
            if_not_exists=True,
        )
