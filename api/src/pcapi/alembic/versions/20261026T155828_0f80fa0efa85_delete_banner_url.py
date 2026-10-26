"""Delete banner url as it is replaced by a property using banner id"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "0f80fa0efa85"
down_revision = "2bc5d29e2492"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.drop_column("google_places_info", "bannerUrl")


def downgrade() -> None:
    op.add_column("google_places_info", sa.Column("bannerUrl", sa.TEXT(), autoincrement=False, nullable=True))
