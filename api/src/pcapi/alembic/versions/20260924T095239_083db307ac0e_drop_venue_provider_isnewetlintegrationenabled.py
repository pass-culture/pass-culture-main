"""Drop VenueProvider.isNewEtlIntegrationEnabled"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "083db307ac0e"
down_revision = "058c27483eab"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.drop_column("venue_provider", "isNewEtlIntegrationEnabled")


def downgrade() -> None:
    op.add_column(
        "venue_provider", sa.Column("isNewEtlIntegrationEnabled", sa.BOOLEAN(), autoincrement=False, nullable=True)
    )
