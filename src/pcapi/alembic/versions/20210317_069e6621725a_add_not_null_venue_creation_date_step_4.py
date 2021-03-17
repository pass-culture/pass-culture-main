"""add_not_null_venue_creation_date_step_4

Revision ID: 069e6621725a
Revises: 182e2a6284e0
Create Date: 2021-03-17 17:27:57.894738

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "069e6621725a"
down_revision = "182e2a6284e0"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_constraint("date_created_not_null_constraint", table_name="venue")


def downgrade() -> None:
    op.execute(
        """
            ALTER TABLE venue ADD CONSTRAINT date_created_not_null_constraint CHECK ("dateCreated" IS NOT NULL) NOT VALID;
        """
    )
