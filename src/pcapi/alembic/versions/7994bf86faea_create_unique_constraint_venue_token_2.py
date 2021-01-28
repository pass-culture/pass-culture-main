"""Add unique constraint on venue.validationToken (Step 2/2)

Revision ID: 7994bf86faea
Revises: 85adf538245f
Create Date: 2021-01-25 19:13:28.102402

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "7994bf86faea"
down_revision = "85adf538245f"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
            ALTER TABLE venue ADD CONSTRAINT validation_token_unique_key UNIQUE USING INDEX idx_venue_validation_token;
        """
    )


def downgrade():
    op.drop_constraint("validation_token_unique_key", "venue")
