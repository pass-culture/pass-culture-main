"""Set collective_offer offerVenue nullable"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "ce7379e58a5f"
down_revision = "3aa9d6b0a643"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.alter_column(
        "collective_offer", "offerVenue", existing_type=postgresql.JSONB(astext_type=sa.Text()), nullable=True
    )


def downgrade() -> None:
    op.alter_column(
        "collective_offer", "offerVenue", existing_type=postgresql.JSONB(astext_type=sa.Text()), nullable=False
    )
