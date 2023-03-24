"""Add NOT NULL constraint on "booking.userId" (step 3 of 4)"""
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "558feec91836"
down_revision = "f1e0b83e0b42"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column("booking", "userId", nullable=False)


def downgrade() -> None:
    op.alter_column("booking", "userId", nullable=True)
