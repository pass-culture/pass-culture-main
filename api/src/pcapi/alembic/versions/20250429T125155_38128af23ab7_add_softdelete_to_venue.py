"""Add isSoftDeleted to Venue"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "38128af23ab7"
down_revision = "2720029af088"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.add_column("venue", sa.Column("isSoftDeleted", sa.Boolean(), server_default=sa.text("false"), nullable=False))


def downgrade() -> None:
    op.drop_column("venue", "isSoftDeleted")
