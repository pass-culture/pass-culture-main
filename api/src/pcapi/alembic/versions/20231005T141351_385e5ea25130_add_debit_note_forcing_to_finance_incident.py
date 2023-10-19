"""Save debit note forcing choice as a boolean in FinanceIncident model
"""
from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "385e5ea25130"
down_revision = "654f1c1c4da3"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("finance_incident", sa.Column("forceDebitNote", sa.Boolean(), server_default="false", nullable=False))


def downgrade() -> None:
    op.drop_column("finance_incident", "forceDebitNote")
