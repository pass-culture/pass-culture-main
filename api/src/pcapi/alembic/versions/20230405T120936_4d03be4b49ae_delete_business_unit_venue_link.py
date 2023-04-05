"""Delete business_unit_venue_link table"""
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "4d03be4b49ae"
down_revision = "599139fa7c52"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("drop table if exists business_unit_venue_link")


def downgrade() -> None:
    pass  # there is no point in restoring the table
