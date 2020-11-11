"""add_provider_enabled_for_pro_and_require_provider_identifier

Revision ID: 035f0ee8ea70
Revises: d4c38884d642
Create Date: 2019-06-25 12:12:52.207776

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
from sqlalchemy.sql import expression


revision = "035f0ee8ea70"
down_revision = "d4c38884d642"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "provider", sa.Column("enabledForPro", sa.Boolean(), nullable=False, server_default=expression.false())
    )
    op.add_column(
        "provider",
        sa.Column("requireProviderIdentifier", sa.Boolean(), nullable=False, server_default=expression.true()),
    )


def downgrade():
    op.drop_column("provider", "enabledForPro")
    op.drop_column("provider", "requireProviderIdentifier")
