"""Add column: venue.validationStatus"""

import sqlalchemy as sa
from alembic import op

from pcapi.core.offerers.models import VenueValidationStatus
from pcapi.utils.db import MagicEnum


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "05c126405692"
down_revision = "23ced5c9120d"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.add_column("venue", sa.Column("validationStatus", MagicEnum(VenueValidationStatus), nullable=True))


def downgrade() -> None:
    op.drop_column("venue", "validationStatus")
