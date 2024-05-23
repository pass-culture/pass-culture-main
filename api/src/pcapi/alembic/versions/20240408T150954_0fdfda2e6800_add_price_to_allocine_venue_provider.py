"""Add price column to AllocineVenueProvider (1/2)
"""

from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "0fdfda2e6800"
down_revision = "2850f548b073"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.add_column("allocine_venue_provider", sa.Column("price", sa.Numeric(precision=10, scale=2), nullable=True))


def downgrade() -> None:
    op.drop_column("allocine_venue_provider", "price")
