"""Create orphan dms application latest modification datetime column
"""
from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "4df590d6ffb3"
down_revision = "6cd0e66502d1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("orphan_dms_application", sa.Column("latest_modification_datetime", sa.DateTime(), nullable=True))


def downgrade() -> None:
    op.drop_column("orphan_dms_application", "latest_modification_datetime")
