"""make_departement_code_nullable

Revision ID: 76d2efd6ad7e
Revises: 8e28c5ce97c9
Create Date: 2021-06-28 13:18:24.483480

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "76d2efd6ad7e"
down_revision = "8e28c5ce97c9"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column("user", "departementCode", existing_type=sa.VARCHAR(length=3), nullable=True)


def downgrade():
    op.alter_column("user", "departementCode", existing_type=sa.VARCHAR(length=3), nullable=False)
