"""offer_add_is_educational_field

Revision ID: 6c410aedecbd
Revises: 7e3f507fd0f3
Create Date: 2021-07-08 09:30:38.773988

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "6c410aedecbd"
down_revision = "7e3f507fd0f3"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("offer", sa.Column("isEducational", sa.Boolean(), server_default=sa.text("false"), nullable=False))


def downgrade():
    op.drop_column("offer", "isEducational")
