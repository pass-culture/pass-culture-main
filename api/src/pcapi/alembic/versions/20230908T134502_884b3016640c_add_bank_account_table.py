"""
Add BankAccount table
"""

from alembic import op
import sqlalchemy as sa

from pcapi.core.finance.models import BankAccountApplicationStatus
from pcapi.utils.db import MagicEnum


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "884b3016640c"
down_revision = "b09c37d295a9"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "bank_account",
        sa.Column("isActive", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("label", sa.String(100), nullable=False),
        sa.Column("offererId", sa.BigInteger(), nullable=False),
        sa.Column("iban", sa.String(length=27), nullable=False),
        sa.Column("bic", sa.String(length=11), nullable=False),
        sa.Column("dsApplicationId", sa.BigInteger(), nullable=True),
        sa.Column("status", MagicEnum(BankAccountApplicationStatus), nullable=False),
        sa.Column("dateCreated", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.Column("dateLastStatusUpdate", sa.DateTime()),
        sa.ForeignKeyConstraint(["offererId"], ["offerer.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("dsApplicationId", name="unique_dsapplicationid_per_bank_account"),
    )
    op.create_index(op.f("ix_bank_account_offererId"), "bank_account", ["offererId"], unique=False)

    # Ensuring backward compatibility with our accounting software
    op.execute(
        """
        ALTER SEQUENCE public.bank_account_id_seq RESTART WITH 100000 
    """
    )


def downgrade() -> None:
    op.drop_table("bank_account")
