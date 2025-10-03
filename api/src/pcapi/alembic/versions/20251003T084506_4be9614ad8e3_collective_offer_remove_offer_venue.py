"""Remove collective_offer offerVenue"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "4be9614ad8e3"
down_revision = "e66cb8cfa231"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.drop_column("collective_offer", "offerVenue")


def downgrade() -> None:
    op.add_column(
        "collective_offer",
        sa.Column("offerVenue", postgresql.JSONB(astext_type=sa.Text()), autoincrement=False, nullable=True),
    )
