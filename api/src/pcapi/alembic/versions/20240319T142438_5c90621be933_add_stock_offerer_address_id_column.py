"""Add stock.offererAddressId column"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "5c90621be933"
down_revision = "afa2a84f772d"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("stock", sa.Column("offererAddressId", sa.BigInteger(), nullable=True))


def downgrade() -> None:
    op.drop_column("stock", "offererAddressId")
