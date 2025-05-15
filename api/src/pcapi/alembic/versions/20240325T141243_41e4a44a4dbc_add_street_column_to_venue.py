"""Add "street" column to "venue" table."""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "41e4a44a4dbc"
down_revision = "ed9648801317"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("venue", sa.Column("street", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("venue", "street")
