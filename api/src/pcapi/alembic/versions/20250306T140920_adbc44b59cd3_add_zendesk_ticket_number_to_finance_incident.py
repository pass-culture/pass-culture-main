"""
Add zendeskId column to finance_incident table
"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "adbc44b59cd3"
down_revision = "8868d0c16c76"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.add_column("finance_incident", sa.Column("zendeskId", sa.BigInteger(), nullable=True))


def downgrade() -> None:
    op.drop_column("finance_incident", "zendeskId")
