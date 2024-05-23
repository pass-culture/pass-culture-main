"""Make AllocineVenueProvider.price non-null
"""

from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "12f6f068d2bc"
down_revision = "6733d62e9059"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.alter_column("allocine_venue_provider", "price", existing_type=sa.NUMERIC(precision=10, scale=2), nullable=False)


def downgrade() -> None:
    op.alter_column("allocine_venue_provider", "price", existing_type=sa.NUMERIC(precision=10, scale=2), nullable=True)
