"""
Add `lastCegidSyncDate` field to BankAccount table
"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "58f3ca2882c6"
down_revision = "90128ccd108a"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.add_column("bank_account", sa.Column("lastCegidSyncDate", sa.DateTime(), nullable=True))


def downgrade() -> None:
    op.drop_column("bank_account", "lastCegidSyncDate")
