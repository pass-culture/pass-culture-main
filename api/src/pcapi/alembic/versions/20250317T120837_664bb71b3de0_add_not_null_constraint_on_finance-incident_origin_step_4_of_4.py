"""Add NOT NULL constraint on "finance_incident.origin" (step 4 of 4)"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "664bb71b3de0"
down_revision = "e7310a92efcf"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.drop_constraint("finance_incident_origin_not_null_constraint", table_name="finance_incident")


def downgrade() -> None:
    op.execute(
        """ALTER TABLE "finance_incident" ADD CONSTRAINT "finance_incident_origin_not_null_constraint" CHECK ("origin" IS NOT NULL) NOT VALID"""
    )
