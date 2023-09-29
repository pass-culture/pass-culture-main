"""
Add bankAccountId column to action_history table
"""
from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "d41989bc9019"
down_revision = "14e9b22809ef"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("action_history", sa.Column("bankAccountId", sa.BigInteger(), nullable=True))
    op.create_index(op.f("ix_action_history_bankAccountId"), "action_history", ["bankAccountId"], unique=False)
    op.create_foreign_key(
        "action_history_bankAccountId_fkey",
        "action_history",
        "bank_account",
        ["bankAccountId"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    op.drop_constraint("action_history_bankAccountId_fkey", "action_history", type_="foreignkey")
    op.drop_index(op.f("ix_action_history_bankAccountId"), table_name="action_history")
    op.drop_column("action_history", "bankAccountId")
