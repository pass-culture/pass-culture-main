"""Drop AllocineVenueProviderPriceRule table
"""

from alembic import op
import sqlalchemy as sa


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "0126d932677e"
down_revision = "e6c2d152ff40"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.drop_table("allocine_venue_provider_price_rule")
    op.execute("DROP TYPE IF EXISTS pricerule")


def downgrade() -> None:
    op.create_table(
        "allocine_venue_provider_price_rule",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("priceRule", sa.Enum("default", name="pricerule"), nullable=False),
        sa.Column("allocineVenueProviderId", sa.BigInteger(), nullable=False),
        sa.Column("price", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.ForeignKeyConstraint(["allocineVenueProviderId"], ["allocine_venue_provider.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("allocineVenueProviderId", "priceRule", name="unique_allocine_venue_provider_price_rule"),
    )
    op.create_index(
        op.f("ix_allocine_venue_provider_price_rule_allocineVenueProviderId"),
        "allocine_venue_provider_price_rule",
        ["allocineVenueProviderId"],
        unique=False,
    )
    op.execute(
        """
        INSERT INTO allocine_venue_provider_price_rule ("allocineVenueProviderId", "price", "priceRule")
        SELECT id, price, 'default'
        FROM allocine_venue_provider
        """
    )
