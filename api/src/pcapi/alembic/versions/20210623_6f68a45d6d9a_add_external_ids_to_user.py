"""add_external_ids_to_user

Revision ID: 6f68a45d6d9a
Revises: 2e918169bb66
Create Date: 2021-06-23 16:10:29.078200

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "6f68a45d6d9a"
down_revision = "2e918169bb66"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "user", sa.Column("externalIds", postgresql.JSONB(astext_type=sa.Text()), server_default="{}", nullable=True)
    )


def downgrade():
    op.drop_column("user", "externalIds")
