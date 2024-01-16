"""
Add isVisibleInApp to Venue
"""

from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "d118574a7888"
down_revision = "d02672d59311"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "venue", sa.Column("isVisibleInApp", sa.Boolean(), nullable=False, server_default=sa.sql.expression.true())
    )


def downgrade() -> None:
    op.drop_column("venue", "isVisibleInApp")
