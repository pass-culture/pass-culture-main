"""Add description text to offer_meta_Data for offer video"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "44509d16b9bf"
down_revision = "8b1f851608bb"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.add_column("offer_meta_data", sa.Column("videoDescription", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("offer_meta_data", "videoDescription")
