"""cascade for venue_criterion_criterionId
"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "4406f656b314"
down_revision = "95e10dd9db7a"
branch_labels = None
depends_on = None


CONSTRAINT_NAME = "venue_criterion_criterionId_fkey"


def upgrade():
    op.execute("SET SESSION statement_timeout = '300s'")

    # Re-create foreign keys for venue_criterion
    op.drop_constraint(CONSTRAINT_NAME, "venue_criterion", type_="foreignkey")
    op.create_foreign_key(CONSTRAINT_NAME, "venue_criterion", "criterion", ["criterionId"], ["id"], ondelete="CASCADE")


def downgrade():
    op.drop_constraint(CONSTRAINT_NAME, "venue_criterion", type_="foreignkey")
    op.create_foreign_key(CONSTRAINT_NAME, "venue_criterion", "criterion", ["criterionId"], ["id"])
