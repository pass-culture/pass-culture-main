"""Remove collective_offer_template offerVenue"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "5376ec9dfdf6"
down_revision = "4be9614ad8e3"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.drop_column("collective_offer_template", "offerVenue")


def downgrade() -> None:
    op.add_column(
        "collective_offer_template",
        sa.Column("offerVenue", postgresql.JSONB(astext_type=sa.Text()), autoincrement=False, nullable=True),
    )
