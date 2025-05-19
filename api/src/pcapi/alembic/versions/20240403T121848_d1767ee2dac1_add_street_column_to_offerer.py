"""Add street column to offerer table"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "d1767ee2dac1"
down_revision = "41e4a44a4dbc"
branch_labels: tuple | None = None
depends_on: tuple | None = None


def upgrade() -> None:
    op.add_column("offerer", sa.Column("street", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("offerer", "street")
