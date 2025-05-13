"""Add NOT NULL constraint on "address.street" (step 3 of 4)"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "2957c0896d6d"
down_revision = "9586c72d6f2c"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.alter_column("address", "street", nullable=False)


def downgrade() -> None:
    op.alter_column("address", "street", nullable=True)
