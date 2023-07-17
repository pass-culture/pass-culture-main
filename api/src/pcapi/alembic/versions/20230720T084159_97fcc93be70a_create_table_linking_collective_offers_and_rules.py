"""Create table to link collective offers to the rules that flagged them
"""
from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "97fcc93be70a"
down_revision = "97536d00f184"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "validation_rule_collective_offer_link",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("ruleId", sa.BigInteger(), nullable=False),
        sa.Column("collectiveOfferId", sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(["collectiveOfferId"], ["collective_offer.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["ruleId"], ["offer_validation_rule.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("validation_rule_collective_offer_link")
