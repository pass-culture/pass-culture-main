"""
add `status` field to `Invoice` model
"""

import sqlalchemy as sa
from alembic import op

from pcapi.core.finance.models import InvoiceStatus
from pcapi.utils.db import MagicEnum


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "b5c2c74ed9e5"
down_revision = "7cd334485a55"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.add_column("invoice", sa.Column("status", MagicEnum(InvoiceStatus), nullable=True))


def downgrade() -> None:
    op.drop_column("invoice", "status")
