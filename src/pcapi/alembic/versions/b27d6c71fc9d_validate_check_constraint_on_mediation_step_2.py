"""Validate check_constraint on mediation.offerId (Step 2/4 to add not null constraint)

Revision ID: b27d6c71fc9d
Revises: b295261d5da0
Create Date: 2021-01-22 10:12:32.939250

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "b27d6c71fc9d"
down_revision = "b295261d5da0"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TABLE mediation VALIDATE CONSTRAINT mediation_offerid_not_null_constraint;")


def downgrade() -> None:
    pass
