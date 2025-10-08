"""Add columns to offerer_address table: type and venueId"""

import sqlalchemy as sa
from alembic import op

from pcapi.core.offerers.models import LocationType
from pcapi.utils.db import MagicEnum


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "d5f66de2af3d"
down_revision = "e429a884bfe0"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.add_column("offerer_address", sa.Column("type", MagicEnum(LocationType), nullable=True))
    op.add_column("offerer_address", sa.Column("venueId", sa.BigInteger(), nullable=True))
    op.create_foreign_key(
        "offerer_address_venueId_fkey",
        "offerer_address",
        "venue",
        ["venueId"],
        ["id"],
        ondelete="CASCADE",
        postgresql_not_valid=True,
    )


def downgrade() -> None:
    op.drop_column("offerer_address", "venueId")
    op.drop_column("offerer_address", "type")
