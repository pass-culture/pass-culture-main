"""Add NOT NULL constraint on "collective_stock.servicePrice" (step 3 of 4)"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "d821984fa9f3"
down_revision = "f983a414bf8c"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.alter_column("collective_stock", "servicePrice", nullable=False)


def downgrade() -> None:
    op.alter_column("collective_stock", "servicePrice", nullable=True)
