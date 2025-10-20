"""Add activity to Venue (represents a Venue's main business activity)"""

import sqlalchemy as sa
from alembic import op

from pcapi.core.offerers.models import Activity
from pcapi.utils.db import MagicEnum


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "1ed8548280cd"
down_revision = "d5f66de2af3d"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.add_column("venue", sa.Column("activity", MagicEnum(Activity), nullable=True))


def downgrade() -> None:
    op.drop_column("venue", "activity")
