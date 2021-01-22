"""Add check_constraint on mediation.offerId (Step 1/4 to add not null constraint)

Revision ID: b295261d5da0
Revises: 06a7f387d996
Create Date: 2021-01-22 10:09:41.533226

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "b295261d5da0"
down_revision = "06a7f387d996"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
             ALTER TABLE mediation ADD CONSTRAINT mediation_offerid_not_null_constraint CHECK ("offerId" IS NOT NULL) NOT VALID;
         """
    )


def downgrade() -> None:
    op.drop_constraint("mediation_offerid_not_null_constraint", table_name="mediation")
