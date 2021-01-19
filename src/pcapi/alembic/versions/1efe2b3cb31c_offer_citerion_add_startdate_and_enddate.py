"""offer_citerion_add_startDate_and_endDate

Revision ID: 1efe2b3cb31c
Revises: 6846a3873abb
Create Date: 2021-01-19 13:16:55.260365

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "1efe2b3cb31c"
down_revision = "6846a3873abb"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("criterion", sa.Column("endDateTime", sa.DateTime, nullable=True))
    op.execute("COMMIT")
    op.add_column("criterion", sa.Column("startDateTime", sa.DateTime, nullable=True))
    op.execute("COMMIT")


def downgrade():
    op.drop_column("criterion", "endDateTime")
    op.drop_column("criterion", "startDateTime")
