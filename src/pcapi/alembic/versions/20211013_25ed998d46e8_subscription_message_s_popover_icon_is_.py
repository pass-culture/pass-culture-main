"""Subscription message's popover icon is optional
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "25ed998d46e8"
down_revision = "2d5bcf0c4a22"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column("beneficiary_subscription_message", "popOverIcon", existing_type=sa.TEXT(), nullable=True)


def downgrade() -> None:
    op.alter_column("beneficiary_subscription_message", "popOverIcon", existing_type=sa.TEXT(), nullable=False)
