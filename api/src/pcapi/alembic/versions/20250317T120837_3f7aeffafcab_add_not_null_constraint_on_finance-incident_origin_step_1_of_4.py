"""Add NOT NULL constraint on "finance_incident.origin" (step 1 of 4)"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "3f7aeffafcab"
down_revision = "7e61bd90eaae"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE "finance_incident" DROP CONSTRAINT IF EXISTS "finance_incident_origin_not_null_constraint";
        ALTER TABLE "finance_incident" ADD CONSTRAINT "finance_incident_origin_not_null_constraint" CHECK ("origin" IS NOT NULL) NOT VALID;
        """
    )


def downgrade() -> None:
    op.drop_constraint("finance_incident_origin_not_null_constraint", table_name="finance_incident")
