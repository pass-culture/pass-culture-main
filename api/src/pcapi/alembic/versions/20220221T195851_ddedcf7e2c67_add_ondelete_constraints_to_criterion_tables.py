"""add ondelete constraints to criterion tables
"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "ddedcf7e2c67"
down_revision = "e9ddaad94160"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("SET SESSION statement_timeout = '300s'")

    # Re-create foreign keys for offer_criterion
    op.drop_constraint("offer_criterion_criterionId_fkey", "offer_criterion", type_="foreignkey")
    op.drop_constraint("offer_criterion_offerId_fkey", "offer_criterion", type_="foreignkey")

    op.create_foreign_key(None, "offer_criterion", "criterion", ["criterionId"], ["id"], ondelete="CASCADE")
    op.create_foreign_key(None, "offer_criterion", "offer", ["offerId"], ["id"], ondelete="CASCADE")

    # Re-create foreign keys for venue_criterion
    op.drop_constraint("venue_criterion_criterionId_fkey", "venue_criterion", type_="foreignkey")
    op.drop_constraint("venue_criterion_venueId_fkey", "venue_criterion", type_="foreignkey")

    op.create_foreign_key(None, "venue_criterion", "venue", ["venueId"], ["id"], ondelete="CASCADE")
    op.create_foreign_key(None, "venue_criterion", "criterion", ["criterionId"], ["id"], ondelete="CASCADE")


def downgrade():
    op.drop_constraint(None, "venue_criterion", type_="foreignkey")
    op.drop_constraint(None, "venue_criterion", type_="foreignkey")

    op.create_foreign_key("venue_criterion_venueId_fkey", "venue_criterion", "venue", ["venueId"], ["id"])
    op.create_foreign_key("venue_criterion_criterionId_fkey", "venue_criterion", "criterion", ["criterionId"], ["id"])

    op.drop_constraint(None, "offer_criterion", type_="foreignkey")
    op.drop_constraint(None, "offer_criterion", type_="foreignkey")

    op.create_foreign_key("offer_criterion_offerId_fkey", "offer_criterion", "offer", ["offerId"], ["id"])
    op.create_foreign_key("offer_criterion_criterionId_fkey", "offer_criterion", "criterion", ["criterionId"], ["id"])
