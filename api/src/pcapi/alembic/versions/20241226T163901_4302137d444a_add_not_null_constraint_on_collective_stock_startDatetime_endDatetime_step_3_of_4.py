"""
Add NOT NULL constraint on "collective_stock.startDatetime" and "collective_stock.endDatetime" (step 3 of 4)
"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "4302137d444a"
down_revision = "89d6c28597ef"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.alter_column("collective_stock", "startDatetime", nullable=False)
    op.alter_column("collective_stock", "endDatetime", nullable=False)


def downgrade() -> None:
    op.alter_column("collective_stock", "startDatetime", nullable=True)
    op.alter_column("collective_stock", "endDatetime", nullable=True)
