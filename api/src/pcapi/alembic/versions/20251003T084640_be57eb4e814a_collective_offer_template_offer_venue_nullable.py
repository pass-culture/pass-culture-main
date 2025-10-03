"""Set collective_offer_template offerVenue nullable"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "be57eb4e814a"
down_revision = "ce7379e58a5f"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.alter_column(
        "collective_offer_template", "offerVenue", existing_type=postgresql.JSONB(astext_type=sa.Text()), nullable=True
    )


def downgrade() -> None:
    op.alter_column(
        "collective_offer_template", "offerVenue", existing_type=postgresql.JSONB(astext_type=sa.Text()), nullable=False
    )
