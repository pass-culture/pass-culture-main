"""Add unique constraint on venue.validationToken (Step 1/2)

Revision ID: 9a2cd2388d90
Revises: e7b46b06f6dd
Create Date: 2021-01-25 17:03:24.375376

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "9a2cd2388d90"
down_revision = "e7b46b06f6dd"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("COMMIT;")
    op.execute(
        """
        CREATE UNIQUE INDEX CONCURRENTLY idx_venue_validation_token ON venue ("validationToken");
        """
    )


def downgrade():
    # when the step_2 validation_token_unique_key is dropped, there is no more index
    pass
