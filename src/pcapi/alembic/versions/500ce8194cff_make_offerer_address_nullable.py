"""make offerer address nullable

Revision ID: 500ce8194cff
Revises: 74313f42daf9
Create Date: 2018-12-03 17:24:05.117802

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "500ce8194cff"
down_revision = "74313f42daf9"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column("offerer", "address", nullable=True)


def downgrade():
    op.execute("UPDATE offerer SET address='' WHERE address IS NULL")
    op.alter_column("offerer", "address", nullable=False)
