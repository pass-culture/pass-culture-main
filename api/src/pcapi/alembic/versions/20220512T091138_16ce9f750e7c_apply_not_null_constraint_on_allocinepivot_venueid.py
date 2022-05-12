"""apply not-null constraint on allocine_pivot.venueId
"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "16ce9f750e7c"
down_revision = "3c19643259f9"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TABLE allocine_pivot VALIDATE CONSTRAINT venue_id_not_null_constraint;")


def downgrade() -> None:
    pass
