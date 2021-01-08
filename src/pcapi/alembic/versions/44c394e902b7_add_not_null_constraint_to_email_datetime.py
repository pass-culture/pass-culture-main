"""Add not null constraint to email.datetime # step 1/4

Revision ID: 44c394e902b7
Revises: 77c4edf7c1fe
Create Date: 2021-01-08 09:40:01.454350

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "44c394e902b7"
down_revision = "77c4edf7c1fe"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
            ALTER TABLE email ADD CONSTRAINT datetime_not_null_constraint CHECK ("datetime" IS NOT NULL) NOT VALID;
        """
    )


def downgrade():
    op.execute(
        """
            ALTER TABLE email DROP CONSTRAINT datetime_not_null_constraint;
        """
    )
