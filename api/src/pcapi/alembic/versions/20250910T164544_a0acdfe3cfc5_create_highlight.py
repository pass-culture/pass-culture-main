"""Add Highlight table"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "a0acdfe3cfc5"
down_revision = "aae08bded987"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.create_table(
        "highlight",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("availability_timespan", postgresql.TSRANGE(), nullable=False),
        sa.Column("highlight_timespan", postgresql.TSRANGE(), nullable=False),
        sa.Column("mediation_uuid", sa.Text(), nullable=False),
        sa.CheckConstraint('length("description") <= 2000'),
        sa.CheckConstraint('length("mediation_uuid") <= 100'),
        sa.CheckConstraint('length("name") <= 200'),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("mediation_uuid"),
    )


def downgrade() -> None:
    op.drop_table("highlight", if_exists=True)
