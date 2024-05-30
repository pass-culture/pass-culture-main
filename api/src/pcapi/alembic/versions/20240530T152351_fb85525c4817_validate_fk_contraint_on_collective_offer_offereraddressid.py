"""Validate CollectiveOffer.offererAddressId FK constraint
"""

from alembic import op
from sqlalchemy import text


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "fb85525c4817"
down_revision = "06ecb5800626"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute(text("""ALTER TABLE collective_offer VALIDATE CONSTRAINT "collective_offer_offererAddressId_fkey" """))


def downgrade() -> None:
    # Nothing to downgrade
    pass
