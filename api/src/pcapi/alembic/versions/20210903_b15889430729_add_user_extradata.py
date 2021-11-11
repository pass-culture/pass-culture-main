"""add user.extraData

Revision ID: b15889430729
Revises: 7ec4136ab598
Create Date: 2021-09-03 07:05:28.624210

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "b15889430729"
down_revision = "7ec4136ab598"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "user", sa.Column("extraData", postgresql.JSONB(astext_type=sa.Text()), server_default="{}", nullable=True)
    )


def downgrade():
    op.drop_column("user", "extraData")
