"""
Add bank_account_status_history
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from pcapi.core.finance.models import BankAccountApplicationStatus
from pcapi.utils.db import MagicEnum


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "705d56381bae"
down_revision = "c56e5591f7b5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "bank_account_status_history",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("bankAccountId", sa.BigInteger(), nullable=False),
        sa.Column(
            "status",
            MagicEnum(BankAccountApplicationStatus),
            nullable=False,
        ),
        sa.Column("timespan", postgresql.TSRANGE(), nullable=False),
        postgresql.ExcludeConstraint((sa.column("bankAccountId"), "="), (sa.column("timespan"), "&&"), using="gist"),
        sa.ForeignKeyConstraint(["bankAccountId"], ["bank_account.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_bank_account_status_history_bankAccountId"),
        "bank_account_status_history",
        ["bankAccountId"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_table("bank_account_status_history")
