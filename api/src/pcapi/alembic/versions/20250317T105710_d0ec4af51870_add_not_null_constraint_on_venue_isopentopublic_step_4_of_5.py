"""Add NOT NULL constraint on "venue.isOpenToPublic" (step 4 of 5)"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "d0ec4af51870"
down_revision = "cc5f6d0d8121"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.alter_column("venue", "isOpenToPublic", nullable=False)


def downgrade() -> None:
    op.alter_column("venue", "isOpenToPublic", nullable=True)
