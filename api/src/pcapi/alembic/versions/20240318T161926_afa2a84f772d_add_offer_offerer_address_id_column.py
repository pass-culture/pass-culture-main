"""Add offer.offererAddressId column"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "afa2a84f772d"
down_revision = "1a30851c9eac"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("offer", sa.Column("offererAddressId", sa.BigInteger(), nullable=True))


def downgrade() -> None:
    op.drop_column("offer", "offererAddressId")
