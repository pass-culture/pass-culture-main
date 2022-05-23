"""remove unused constraint on allocine_pivot
"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "64d4d0dabdd2"
down_revision = "e7b45d73db12"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_constraint("venue_id_not_null_constraint", table_name="allocine_pivot")


def downgrade() -> None:
    op.execute(
        """
            ALTER TABLE allocine_pivot ADD CONSTRAINT venue_id_not_null_constraint CHECK ("venueId" IS NOT NULL) NOT VALID;
        """
    )
