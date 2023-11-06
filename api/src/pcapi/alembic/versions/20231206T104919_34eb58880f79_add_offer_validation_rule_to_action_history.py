"""Add OfferValidationRule to ActionHistory
"""
from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "34eb58880f79"
down_revision = "3ab07dc09e34"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("action_history", sa.Column("ruleId", sa.BigInteger(), nullable=True))
    op.create_index(op.f("ix_action_history_ruleId"), "action_history", ["ruleId"], unique=False)
    op.create_foreign_key(
        "action_history_ruleId_fkey", "action_history", "offer_validation_rule", ["ruleId"], ["id"], ondelete="CASCADE"
    )


def downgrade() -> None:
    op.drop_constraint("action_history_ruleId_fkey", "action_history", type_="foreignkey")
    op.drop_index(op.f("ix_action_history_ruleId"), table_name="action_history")
    op.drop_column("action_history", "ruleId")
