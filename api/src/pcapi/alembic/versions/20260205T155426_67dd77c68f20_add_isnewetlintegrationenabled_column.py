"""Add `isNewEtlIntegrationEnabled` column to `venue_provider` table"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "67dd77c68f20"
down_revision = "a94a6d202f5a"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.add_column("venue_provider", sa.Column("isNewEtlIntegrationEnabled", sa.Boolean(), nullable=True))


def downgrade() -> None:
    op.drop_column("venue_provider", "isNewEtlIntegrationEnabled")
