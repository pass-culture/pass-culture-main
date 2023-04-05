"""Delete business_unit table"""
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "4b5ddbcf6b11"
down_revision = "2c3c118d8e89"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("drop table if exists business_unit")


def downgrade() -> None:
    pass  # there is no point in restoring the table
