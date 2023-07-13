"""Add `status_pricing_point_ordering_date_check` constraint on `finance_event` table
"""
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "96e489262a9a"
down_revision = "1a69e5c1767c"
branch_labels = None
depends_on = None


CONSTRAINT_NAME = "status_pricing_point_ordering_date_check"


def upgrade() -> None:
    op.execute(
        f"""
        ALTER TABLE finance_event
        ADD CONSTRAINT {CONSTRAINT_NAME}
        CHECK (
            (
              status = 'pending'
              AND "pricingPointId" IS NULL
              AND "pricingOrderingDate" IS NULL
            ) OR (
              "pricingPointId" IS NOT NULL
              AND "pricingOrderingDate" IS NOT NULL
            )
            OR status in ('cancelled', 'not to be priced')
        )
        """
    )


def downgrade() -> None:
    op.execute(f"""ALTER TABLE finance_event DROP CONSTRAINT {CONSTRAINT_NAME}""")
