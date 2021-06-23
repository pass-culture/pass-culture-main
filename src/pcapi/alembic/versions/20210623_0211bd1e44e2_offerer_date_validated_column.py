"""offerer_date_validated_column

Revision ID: 0211bd1e44e2
Revises: 84706f806e3d
Create Date: 2021-06-23 08:49:44.335248

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0211bd1e44e2"
down_revision = "2e918169bb66"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("offerer", sa.Column("dateValidated", sa.DateTime(), nullable=True))


def downgrade():
    op.drop_column("offerer", "dateValidated")
