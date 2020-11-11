"""add_venue_provider_price_rules

Revision ID: 75f2ccf2be82
Revises: 21ef2b9af5e6
Create Date: 2019-12-11 16:41:30.561830

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
from sqlalchemy import ForeignKey

from pcapi.domain.price_rule import PriceRule


revision = "75f2ccf2be82"
down_revision = "21ef2b9af5e6"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "venue_provider_price_rule",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column("venueProviderId", sa.BigInteger, ForeignKey("venue_provider.id"), nullable=False, index=True),
        sa.Column("priceRule", sa.Enum(PriceRule), nullable=False),
        sa.Column("price", sa.Numeric(10, 2), nullable=False),
    )

    op.create_check_constraint(
        constraint_name="check_price_is_not_negative", table_name="venue_provider_price_rule", condition="price >= 0"
    )

    op.create_unique_constraint(
        "unique_venue_provider_price_rule", "venue_provider_price_rule", ["venueProviderId", "priceRule"]
    )


def downgrade():
    op.drop_table("venue_provider_price_rule")
    op.execute("DROP TYPE PriceRule;")
