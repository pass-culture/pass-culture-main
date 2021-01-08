"""Add not null to email.datetime # step 3/4

Revision ID: 541e87e7b7bb
Revises: eb7d08bda995
Create Date: 2021-01-08 09:50:20.645972

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "541e87e7b7bb"
down_revision = "eb7d08bda995"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column("email", "datetime", nullable=False)


def downgrade():
    op.alter_column("email", "datetime", nullable=True)
