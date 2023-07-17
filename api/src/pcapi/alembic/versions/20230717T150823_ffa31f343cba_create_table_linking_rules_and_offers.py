"""Create table to link offers to the rules that flagged them
"""
from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "ffa31f343cba"
down_revision = "76f3eb18e4c1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "validation_rule_offer_link",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("ruleId", sa.BigInteger(), nullable=False),
        sa.Column("offerId", sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(["offerId"], ["offer.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["ruleId"], ["offer_validation_rule.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("validation_rule_offer_link")
