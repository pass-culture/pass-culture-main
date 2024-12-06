"""Add rejectionReason to collectiveOffer and collectiveOfferTemplate
"""

from alembic import op
import sqlalchemy as sa

from pcapi.core.educational.models import CollectiveOfferRejectionReasons
from pcapi.utils.db import MagicEnum


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "741084b8cec2"
down_revision = "1e2330f8af48"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.add_column(
        "collective_offer", sa.Column("rejectionReason", MagicEnum(CollectiveOfferRejectionReasons), nullable=True)
    )
    op.add_column(
        "collective_offer_template",
        sa.Column("rejectionReason", MagicEnum(CollectiveOfferRejectionReasons), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("collective_offer_template", "rejectionReason")
    op.drop_column("collective_offer", "rejectionReason")
