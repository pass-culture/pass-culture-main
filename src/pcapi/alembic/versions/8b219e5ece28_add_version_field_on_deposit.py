"""add_version_field_on_deposit

Revision ID: 8b219e5ece28
Revises: 55bf0bb6c53b
Create Date: 2020-12-18 15:28:15.415357

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "8b219e5ece28"
down_revision = "55bf0bb6c53b"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("deposit", sa.Column("version", sa.SmallInteger(), nullable=True))


def downgrade() -> None:
    op.drop_column("deposit", "version")
