"""Drop table beneficiary_subscription_message
"""
from alembic import op
import sqlalchemy as sa


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "c1ac03cbcc57"
down_revision = "fe0d250879b4"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_table("beneficiary_subscription_message")


def downgrade() -> None:
    op.create_table(
        "beneficiary_subscription_message",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("dateCreated", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("userId", sa.BigInteger(), nullable=False),
        sa.Column("userMessage", sa.Text(), nullable=False),
        sa.Column("callToActionTitle", sa.Text(), nullable=True),
        sa.Column("callToActionLink", sa.Text(), nullable=True),
        sa.Column("callToActionIcon", sa.Text(), nullable=True),
        sa.Column("popOverIcon", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["userId"], ["user.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_beneficiary_subscription_message_userId"), "beneficiary_subscription_message", ["userId"], unique=False
    )
