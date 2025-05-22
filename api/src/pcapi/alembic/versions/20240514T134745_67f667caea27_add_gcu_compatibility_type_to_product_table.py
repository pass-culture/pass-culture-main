"""Add gcuCompatibilityType to Product table"""

import sqlalchemy as sa
from alembic import op

from pcapi.core.offers.models import GcuCompatibilityType
from pcapi.utils.db import MagicEnum


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "67f667caea27"
down_revision = "6c12bca98549"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.add_column(
        "product",
        sa.Column(
            "gcuCompatibilityType",
            MagicEnum(GcuCompatibilityType),
            default=GcuCompatibilityType.COMPATIBLE,
            server_default=GcuCompatibilityType.COMPATIBLE.value,
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_column("product", "gcuCompatibilityType")
