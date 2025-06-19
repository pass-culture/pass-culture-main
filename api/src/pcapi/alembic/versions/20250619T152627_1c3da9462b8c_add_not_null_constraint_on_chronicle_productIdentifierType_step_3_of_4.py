"""Add NOT NULL constraint on "chronicle.productIdentifierType" (step 3 of 4)"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "1c3da9462b8c"
down_revision = "5ceb90d55919"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.alter_column("chronicle", "productIdentifierType", nullable=False)


def downgrade() -> None:
    op.alter_column("chronicle", "productIdentifierType", nullable=True)
