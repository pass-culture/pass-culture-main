"""add nullable validationStatus to venue"""

import sqlalchemy as sa
from alembic import op

from pcapi.core.offerers.models import ValidationStatus
from pcapi.utils.db import MagicEnum


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "5566d8393bb3"
down_revision = "4c0c60c2ab7d"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.add_column("venue", sa.Column("validationStatus", MagicEnum(ValidationStatus), nullable=True))


def downgrade() -> None:
    op.drop_column("venue", "validationStatus")
