"""Add not null constraint on mediation.offerId (Step 3/4 to add not null constraint)

Revision ID: 7a89c0773774
Revises: b27d6c71fc9d
Create Date: 2021-01-22 10:14:03.844534

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "7a89c0773774"
down_revision = "b27d6c71fc9d"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column("mediation", "offerId", nullable=False)


def downgrade() -> None:
    op.alter_column("mediation", "offerId", nullable=True)
