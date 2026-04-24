"""delete "offer_id" column on "opening_hours" table"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "1356ff1cc2fc"
down_revision = "0fea3fa4c699"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.drop_column("opening_hours", "offerId")


def downgrade() -> None:
    op.add_column("opening_hours", sa.Column("offerId", sa.BIGINT(), autoincrement=False, nullable=True))
