"""add-not-null-booking-venuid-step-1

Revision ID: 289494f36088
Revises: e65789e45741
Create Date: 2021-08-26 15:55:55.148991

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "289494f36088"
down_revision = "e65789e45741"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
            ALTER TABLE booking ADD CONSTRAINT venueid_not_null_constraint CHECK ("venueId" IS NOT NULL) NOT VALID;
        """
    )


def downgrade() -> None:
    op.drop_constraint("venueid_not_null_constraint", table_name="booking")
