"""add_orphan_date_created
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "d1a514ca8bd1"
down_revision = "c7877e6119e7"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("orphan_dms_application", sa.Column("dateCreated", sa.DateTime(), nullable=True))


def downgrade() -> None:
    op.drop_column("orphan_dms_application", "dateCreated")
