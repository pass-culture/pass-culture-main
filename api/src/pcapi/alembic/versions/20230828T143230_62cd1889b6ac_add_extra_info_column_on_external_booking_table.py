"""
Add an `additional_information` column on ExternalBooking table.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "62cd1889b6ac"
down_revision = "eff2f403eaac"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("external_booking", sa.Column("additional_information", postgresql.JSONB(astext_type=sa.Text())))


def downgrade() -> None:
    op.drop_column("external_booking", "additional_information")
