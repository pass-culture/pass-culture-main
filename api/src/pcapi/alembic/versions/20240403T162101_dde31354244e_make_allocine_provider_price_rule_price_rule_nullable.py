"""Make `allocine_provider_price_rule.priceRule` nullable before deletion
"""

from alembic import op
from sqlalchemy.dialects import postgresql


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "dde31354244e"
down_revision = "374e35815645"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.alter_column(
        "allocine_venue_provider_price_rule",
        "priceRule",
        existing_type=postgresql.ENUM("default", name="pricerule"),
        nullable=True,
    )


def downgrade() -> None:
    # Restore previous value, which was always "default".
    op.execute("""update allocine_venue_provider_price_rule set "priceRule" = 'default'""")
    op.alter_column(
        "allocine_venue_provider_price_rule",
        "priceRule",
        existing_type=postgresql.ENUM("default", name="pricerule"),
        nullable=False,
    )
