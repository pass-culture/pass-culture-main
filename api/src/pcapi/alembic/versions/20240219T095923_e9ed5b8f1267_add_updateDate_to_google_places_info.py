"""
add updateDate to google_places_info
"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "e9ed5b8f1267"
down_revision = "3bc3200ec909"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "google_places_info", sa.Column("updateDate", sa.DateTime(), server_default=sa.text("now()"), nullable=False)
    )


def downgrade() -> None:
    op.drop_column("google_places_info", "updateDate")
