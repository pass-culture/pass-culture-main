"""Remove `allocine_provider_price_rule.priceRule` column
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "21aa80d5344f"
down_revision = "e0ade941956f"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.drop_column("allocine_venue_provider_price_rule", "priceRule")


def downgrade() -> None:
    op.add_column(
        "allocine_venue_provider_price_rule",
        sa.Column("priceRule", postgresql.ENUM("default", name="pricerule"), autoincrement=False, nullable=True),
    )
    # Adding a UNIQUE constraint locks the table but:
    # - this is a downgrade migration that is very unlikely to be run;
    # - the table is rarely accessed.
    op.execute("select 1 -- squawk:ignore-next-statement")
    op.create_unique_constraint(
        "unique_allocine_venue_provider_price_rule",
        "allocine_venue_provider_price_rule",
        ["allocineVenueProviderId", "priceRule"],
    )
