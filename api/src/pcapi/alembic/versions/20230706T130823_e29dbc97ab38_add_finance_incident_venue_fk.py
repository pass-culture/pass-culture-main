"""
Add `finance_incident.venueId` foreign key
"""
from alembic import op
import sqlalchemy as sa


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "e29dbc97ab38"
down_revision = "9f5e01a79b73"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("finance_incident", sa.Column("venueId", sa.BigInteger(), nullable=False))
    op.create_foreign_key("finance_incident_venueId_fkey", "finance_incident", "venue", ["venueId"], ["id"])


def downgrade() -> None:
    op.drop_constraint("finance_incident_venueId_fkey", "finance_incident", type_="foreignkey")
    op.drop_column("finance_incident", "venueId")
