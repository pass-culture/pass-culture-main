"""Drop not null constraint on email.datetime # step 4/4

Revision ID: 692f4bd89a83
Revises: 541e87e7b7bb
Create Date: 2021-01-08 09:51:52.800945

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "692f4bd89a83"
down_revision = "541e87e7b7bb"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_constraint("datetime_not_null_constraint", table_name="email")


def downgrade():
    op.execute(
        """
            ALTER TABLE email ADD CONSTRAINT datetime_not_null_constraint CHECK ("datetime" IS NOT NULL) NOT VALID;
        """
    )
