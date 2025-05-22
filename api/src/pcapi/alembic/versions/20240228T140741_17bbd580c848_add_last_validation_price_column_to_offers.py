"""
Add lastValidationPrice column to Offer
"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "17bbd580c848"
down_revision = "fa4755bb92f0"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("offer", sa.Column("lastValidationPrice", sa.Numeric(precision=10, scale=2), nullable=True))


def downgrade() -> None:
    op.drop_column("offer", "lastValidationPrice")
