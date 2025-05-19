"""Add origin and comment fields to finance_incident table"""

import sqlalchemy as sa
from alembic import op

from pcapi.core.finance.models import FinanceIncidentRequestOrigin
from pcapi.utils.db import MagicEnum


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "ddf63ed44a81"
down_revision = "adbc44b59cd3"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.add_column("finance_incident", sa.Column("origin", MagicEnum(FinanceIncidentRequestOrigin), nullable=True))
    op.add_column("finance_incident", sa.Column("comment", sa.Text, nullable=True))


def downgrade() -> None:
    op.drop_column("finance_incident", "origin")
    op.drop_column("finance_incident", "comment")
