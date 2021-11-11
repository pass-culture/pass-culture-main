"""Create subscription messages
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "5129a4e3aabb"
down_revision = "1c48ca792f7d"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "beneficiary_subscription_message",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("dateCreated", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("userId", sa.BigInteger(), nullable=False),
        sa.Column("userMessage", sa.Text(), nullable=False),
        sa.Column("callToActionTitle", sa.Text(), nullable=False),
        sa.Column("callToActionLink", sa.Text(), nullable=False),
        sa.Column("callToActionIcon", sa.Text(), nullable=False),
        sa.Column("popOverIcon", sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(["userId"], ["user.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_beneficiary_subscription_message_userId"), "beneficiary_subscription_message", ["userId"], unique=False
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_beneficiary_subscription_message_userId"), table_name="beneficiary_subscription_message")
    op.drop_table("beneficiary_subscription_message")
