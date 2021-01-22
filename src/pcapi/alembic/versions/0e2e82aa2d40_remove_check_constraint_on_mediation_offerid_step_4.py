"""Remove check constraint on mediation.offerId (Step 4/4 to add not null constraint)

Revision ID: 0e2e82aa2d40
Revises: 7a89c0773774
Create Date: 2021-01-22 10:18:22.695050

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "0e2e82aa2d40"
down_revision = "7a89c0773774"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_constraint("mediation_offerid_not_null_constraint", table_name="mediation")


def downgrade() -> None:
    op.execute(
        """
            ALTER TABLE mediation ADD CONSTRAINT mediation_offerid_not_null_constraint CHECK ("offerId" IS NOT NULL) NOT VALID;
        """
    )
