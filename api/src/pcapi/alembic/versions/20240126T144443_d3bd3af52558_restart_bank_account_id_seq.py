"""Restart bank_account_id_seq at 200_000"""

from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "d3bd3af52558"
down_revision = "ca50ad3c3fd6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER SEQUENCE public.bank_account_id_seq RESTART WITH 200000")


def downgrade() -> None:
    # Nothing to downgrade
    pass
