"""
Drop nullable constraint on beginningDatetime
"""

from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "9d1b6d3edf16"
down_revision = "1ec374800b10"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.alter_column("collective_stock", "beginningDatetime", nullable=True)


def downgrade() -> None:
    op.alter_column("collective_stock", "beginningDatetime", nullable=False)
