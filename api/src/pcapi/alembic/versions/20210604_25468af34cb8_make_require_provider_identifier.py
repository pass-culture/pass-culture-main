"""make_require_provider_identifier_nullable

Revision ID: 25468af34cb8
Revises: e85a73abc5a7
Create Date: 2021-06-04 18:05:43.310800

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "25468af34cb8"
down_revision = "e85a73abc5a7"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column(
        "provider",
        "requireProviderIdentifier",
        existing_type=sa.BOOLEAN(),
        nullable=True,
        existing_server_default=sa.text("true"),
    )


def downgrade():
    op.alter_column(
        "provider",
        "requireProviderIdentifier",
        existing_type=sa.BOOLEAN(),
        nullable=False,
        existing_server_default=sa.text("true"),
    )
