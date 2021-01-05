"""Change feature.name from an enum to a text column

Revision ID: f17831b0a62a
Revises: 1e81fd76a908
Create Date: 2021-01-05 18:05:06.971798

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "f17831b0a62a"
down_revision = "1e81fd76a908"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column("feature", "name", type_=sa.Text())


def downgrade():
    op.execute("ALTER TABLE feature ALTER COLUMN name TYPE featuretoggle USING name::text::featuretoggle")
