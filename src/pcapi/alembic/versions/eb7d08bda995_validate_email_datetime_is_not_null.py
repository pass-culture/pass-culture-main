"""Validate email datetime is not null # step 2/4

Revision ID: eb7d08bda995
Revises: 44c394e902b7
Create Date: 2021-01-08 09:47:23.810498

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "eb7d08bda995"
down_revision = "44c394e902b7"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("ALTER TABLE email VALIDATE CONSTRAINT datetime_not_null_constraint;")


def downgrade():
    pass
