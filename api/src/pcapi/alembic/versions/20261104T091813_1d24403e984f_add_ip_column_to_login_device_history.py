"""Add ipAddress column to login_device_history table."""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "1d24403e984f"
down_revision = "72d7e2638079"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.add_column("login_device_history", sa.Column("ipAddress", postgresql.INET(), nullable=True), if_not_exists=True)


def downgrade() -> None:
    op.drop_column("login_device_history", "ipAddress", if_exists=True)
