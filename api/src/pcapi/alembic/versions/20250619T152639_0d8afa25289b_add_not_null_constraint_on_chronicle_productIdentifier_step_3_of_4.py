"""Add NOT NULL constraint on "chronicle.productIdentifier" (step 3 of 4)"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "0d8afa25289b"
down_revision = "159928eb61a0"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.alter_column("chronicle", "productIdentifier", nullable=False)


def downgrade() -> None:
    op.alter_column("chronicle", "productIdentifier", nullable=True)
