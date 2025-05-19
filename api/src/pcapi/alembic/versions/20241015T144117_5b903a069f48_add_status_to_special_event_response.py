"""Add status column to SpecialEventResponse"""

import sqlalchemy as sa
from alembic import op

from pcapi.core.operations.models import SpecialEventResponseStatus
from pcapi.utils.db import MagicEnum


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "5b903a069f48"
down_revision = "88c4d806c740"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.add_column("special_event_response", sa.Column("status", MagicEnum(SpecialEventResponseStatus), nullable=False))


def downgrade() -> None:
    op.drop_column("special_event_response", "status")
