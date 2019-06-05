"""Add index on lower(user.email)

Revision ID: a6bdec6dde59
Revises: 09857d7d7492
Create Date: 2019-06-05 13:57:19.986598

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a6bdec6dde59'
down_revision = '09857d7d7492'
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
          CREATE INDEX "ix_user_lower_email" ON "user" USING btree (lower("email"));
        """)
    pass


def downgrade():
    op.execute(
        """
          DROP INDEX "ix_user_lower_email";
        """)
    pass
