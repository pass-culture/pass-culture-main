"""Make Criterion.scoreDelta nullable

Revision ID: b00c0a0dec8f
Revises: f460dc2c9f93
Create Date: 2021-02-23 14:53:18.932854

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "b00c0a0dec8f"
down_revision = "f460dc2c9f93"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column("criterion", "scoreDelta", existing_type=sa.INTEGER(), nullable=True)


def downgrade():
    op.alter_column("criterion", "scoreDelta", existing_type=sa.INTEGER(), nullable=False)
