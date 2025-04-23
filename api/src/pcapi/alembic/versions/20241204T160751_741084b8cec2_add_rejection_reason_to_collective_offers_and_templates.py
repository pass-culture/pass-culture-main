"""Add rejectionReason to collectiveOffer and collectiveOfferTemplate"""

from alembic import op
import sqlalchemy as sa

from pcapi.core.educational.models import CollectiveOfferRejectionReason
from pcapi.utils.db import MagicEnum


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "741084b8cec2"
down_revision = "bcf2693c0c2c"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.add_column(
        "collective_offer", sa.Column("rejectionReason", MagicEnum(CollectiveOfferRejectionReason), nullable=True)
    )
    op.add_column(
        "collective_offer_template",
        sa.Column("rejectionReason", MagicEnum(CollectiveOfferRejectionReason), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("collective_offer_template", "rejectionReason")
    op.drop_column("collective_offer", "rejectionReason")
