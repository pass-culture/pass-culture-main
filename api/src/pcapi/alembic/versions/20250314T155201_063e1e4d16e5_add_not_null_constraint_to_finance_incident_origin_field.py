"""Add NOT NULL constraint to finance_incident origin field"""

from alembic import op

from pcapi.core.finance.models import FinanceIncidentRequestOrigin
from pcapi.utils.db import MagicEnum


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "063e1e4d16e5"
down_revision = "7e61bd90eaae"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.alter_column("finance_incident", "origin", existing_type=MagicEnum(FinanceIncidentRequestOrigin), nullable=False)


def downgrade() -> None:
    op.alter_column("finance_incident", "origin", existing_type=MagicEnum(FinanceIncidentRequestOrigin), nullable=True)
