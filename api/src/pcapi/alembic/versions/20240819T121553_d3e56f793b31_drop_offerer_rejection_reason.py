"""drop column: offerer.rejectionReason"""

import sqlalchemy as sa
from alembic import op

from pcapi.core.offerers.models import OffererRejectionReason
from pcapi.utils.db import MagicEnum


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "d3e56f793b31"
down_revision = "fd3e014497e1"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.drop_column("offerer", "rejectionReason")


def downgrade() -> None:
    op.add_column("offerer", sa.Column("rejectionReason", MagicEnum(OffererRejectionReason), nullable=True))
