"""Add NOT NULL constraint on `deposit.version`

Revision ID: 0784847b5e46
Revises: f17831b0a62a
Create Date: 2021-01-08 09:42:56.947827

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0784847b5e46"
down_revision = "f17831b0a62a"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column("deposit", "version", existing_type=sa.SMALLINT(), nullable=False)


def downgrade():
    op.alter_column("deposit", "version", existing_type=sa.SMALLINT(), nullable=True)
