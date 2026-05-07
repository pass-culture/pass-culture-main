"""add nullable state to venue"""

import sqlalchemy as sa
from alembic import op

from pcapi.core.offerers.models import VenueState
from pcapi.utils.db import MagicEnum


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "734b78b841f2"
down_revision = "de0fbd846d9f"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.add_column("venue", sa.Column("state", MagicEnum(VenueState), nullable=True))


def downgrade() -> None:
    op.drop_column("venue", "state")
