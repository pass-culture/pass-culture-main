"""Add future_offer foreign key constraint
"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "2144f7e4df3c"
down_revision = "cbd967876cbb"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE "future_offer" ADD CONSTRAINT "future_offer_offerId" FOREIGN KEY("offerId") REFERENCES offer (id) on delete CASCADE NOT VALID;
        """
    )


def downgrade() -> None:
    op.execute(
        """
        ALTER TABLE IF EXISTS "future_offer" DROP CONSTRAINT IF EXISTS "future_offer_offerId";
        """
    )
