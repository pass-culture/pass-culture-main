"""Populate AllocineVenueProvider.price (2/2)
"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "69f58f589e88"
down_revision = "fbb9ccd03884"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        UPDATE allocine_venue_provider
        SET price = allocine_venue_provider_price_rule.price
        FROM allocine_venue_provider_price_rule
        WHERE allocine_venue_provider.id = allocine_venue_provider_price_rule."allocineVenueProviderId";
        """
    )


def downgrade() -> None:
    pass
