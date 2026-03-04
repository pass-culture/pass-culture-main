"""Add NOT NULL constraint on "pro_advice.venueId" (step 3 of 4)"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "ccc59658611d"
down_revision = "0e5beac55300"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute("select 1 -- squawk:ignore-next-statement")
    op.alter_column("pro_advice", "venueId", nullable=False)


def downgrade() -> None:
    op.alter_column("pro_advice", "venueId", nullable=True)
