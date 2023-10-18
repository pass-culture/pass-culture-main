"""add start-end daterange to collective offer template"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "8425db0af4c1"
down_revision = "385e5ea25130"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("collective_offer_template", sa.Column("dateRange", postgresql.TSRANGE(), nullable=True))
    op.create_unique_constraint(
        "collective_offer_template_unique_daterange", "collective_offer_template", ["dateRange", "id"]
    )
    op.create_check_constraint(
        constraint_name="template_dates_non_empty_daterange",
        table_name="collective_offer_template",
        condition=(
            '"dateRange" is NULL OR ('
            'NOT isempty("dateRange") '
            'AND lower("dateRange") is NOT NULL '
            'AND upper("dateRange") IS NOT NULL '
            'AND lower("dateRange")::date >= "dateCreated"::date)'
        ),
    )


def downgrade() -> None:
    op.drop_constraint("collective_offer_template_unique_daterange", "collective_offer_template", type_="unique")
    op.drop_constraint("template_dates_non_empty_daterange", "collective_offer_template", type_="check")
    op.drop_column("collective_offer_template", "dateRange")
