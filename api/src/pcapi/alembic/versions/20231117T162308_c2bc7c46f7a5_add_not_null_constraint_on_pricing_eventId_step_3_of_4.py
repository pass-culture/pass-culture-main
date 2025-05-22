"""Add NOT NULL constraint on "pricing.eventId" (step 3 of 4)"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "c2bc7c46f7a5"
down_revision = "c1a24da729e5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column("pricing", "eventId", nullable=False)


def downgrade() -> None:
    op.alter_column("pricing", "eventId", nullable=True)
