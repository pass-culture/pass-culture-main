"""Add accessibility to offer_meta_data"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

from pcapi.core.offers import constants as offers_constants
from pcapi.utils.db import MagicEnum


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "a16d6a4bf074"
down_revision = "ebf2d4fcbd43"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.add_column(
        "offer_meta_data",
        sa.Column(
            "accessibility",
            postgresql.ARRAY(MagicEnum(offers_constants.OfferAccessibilityEnum)),
            server_default="{}",
            nullable=True,
        ),
    )


def downgrade() -> None:
    op.drop_column("offer_meta_data", "accessibility")
