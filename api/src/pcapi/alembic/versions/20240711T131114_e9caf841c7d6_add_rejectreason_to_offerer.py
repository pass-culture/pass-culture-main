"""
add rejectionReason to Offerer
"""

from alembic import op
import sqlalchemy as sa

from pcapi.core.offerers.models import OffererRejectionReason
from pcapi.utils.db import MagicEnum


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "e9caf841c7d6"
down_revision = "59d02d648922"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.add_column("offerer", sa.Column("rejectionReason", MagicEnum(OffererRejectionReason), nullable=True))


def downgrade() -> None:
    op.drop_column("offerer", "rejectionReason")
