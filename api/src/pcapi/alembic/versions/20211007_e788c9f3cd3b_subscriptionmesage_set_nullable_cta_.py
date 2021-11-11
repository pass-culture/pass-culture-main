"""SubscriptionMesage : set nullable CTA columns
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "e788c9f3cd3b"
down_revision = "418152da3d41"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column("beneficiary_subscription_message", "callToActionIcon", existing_type=sa.TEXT(), nullable=True)
    op.alter_column("beneficiary_subscription_message", "callToActionLink", existing_type=sa.TEXT(), nullable=True)
    op.alter_column("beneficiary_subscription_message", "callToActionTitle", existing_type=sa.TEXT(), nullable=True)


def downgrade() -> None:
    op.alter_column("beneficiary_subscription_message", "callToActionTitle", existing_type=sa.TEXT(), nullable=False)
    op.alter_column("beneficiary_subscription_message", "callToActionLink", existing_type=sa.TEXT(), nullable=False)
    op.alter_column("beneficiary_subscription_message", "callToActionIcon", existing_type=sa.TEXT(), nullable=False)
