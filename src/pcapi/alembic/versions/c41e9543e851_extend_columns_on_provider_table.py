"""extend_columns_on_provider_table

Revision ID: c41e9543e851
Revises: cff9e82d0558
Create Date: 2019-05-24 12:56:12.550164

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "c41e9543e851"
down_revision = "cff9e82d0558"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column("provider", "name", existing_type=sa.VARCHAR(length=60), type_=sa.VARCHAR(length=90))
    op.alter_column("provider", "localClass", existing_type=sa.VARCHAR(length=30), type_=sa.VARCHAR(length=60))
    pass


def downgrade():
    op.alter_column("provider", "localClass", existing_type=sa.VARCHAR(length=90), type_=sa.VARCHAR(length=60))
    op.alter_column("provider", "localClass", existing_type=sa.VARCHAR(length=60), type_=sa.VARCHAR(length=30))
    pass
