"""add_not_null_venue_creation_date_step_1

Revision ID: 3d149d0afa76
Revises: 08e0af71bcfe
Create Date: 2021-03-17 17:27:43.264186

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "3d149d0afa76"
down_revision = "08e0af71bcfe"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
            ALTER TABLE venue ADD CONSTRAINT date_created_not_null_constraint CHECK ("dateCreated" IS NOT NULL) NOT VALID;
        """
    )


def downgrade() -> None:
    op.drop_constraint("date_created_not_null_constraint", table_name="venue")
