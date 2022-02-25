"""cascade for venue_criterion_venueId
"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "56c6d018551c"
down_revision = "4406f656b314"
branch_labels = None
depends_on = None


CONSTRAINT_NAME = "venue_criterion_venueId_fkey"


def upgrade():
    op.execute("SET SESSION statement_timeout = '300s'")

    # Re-create foreign keys for venue_criterion
    op.drop_constraint(CONSTRAINT_NAME, "venue_criterion", type_="foreignkey")
    op.create_foreign_key(CONSTRAINT_NAME, "venue_criterion", "venue", ["venueId"], ["id"], ondelete="CASCADE")


def downgrade():
    op.drop_constraint(CONSTRAINT_NAME, "venue_criterion", type_="foreignkey")
    op.create_foreign_key(CONSTRAINT_NAME, "venue_criterion", "venue", ["venueId"], ["id"])
