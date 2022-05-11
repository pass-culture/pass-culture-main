"""add not-null constraint on venueId to allocine pivot
"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "3c19643259f9"
down_revision = "d1a514ca8bd1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
            ALTER TABLE allocine_pivot ADD CONSTRAINT venue_id_not_null_constraint CHECK ("venueId" IS NOT NULL) NOT VALID;
        """
    )


def downgrade() -> None:
    op.drop_constraint("venue_id_not_null_constraint", table_name="allocine_pivot")
