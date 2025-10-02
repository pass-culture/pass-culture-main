"""Add NOT NULL constraint on "venue.offererAddressId" (step 3 of 4)"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "a8bd8e8f8db8"
down_revision = "c40115eb390f"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.alter_column("venue", "offererAddressId", nullable=False)


def downgrade() -> None:
    op.alter_column("venue", "offererAddressId", nullable=True)
