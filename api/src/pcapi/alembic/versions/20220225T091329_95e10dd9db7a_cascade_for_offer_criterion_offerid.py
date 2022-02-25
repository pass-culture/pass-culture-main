"""cascade for offer_criterion_offerId
"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "95e10dd9db7a"
down_revision = "ddedcf7e2c67"
branch_labels = None
depends_on = None


CONSTRAINT_NAME = "offer_criterion_offerId_fkey"


def upgrade():
    op.execute("SET SESSION statement_timeout = '300s'")

    # Re-create foreign keys for offer_criterion
    op.drop_constraint(CONSTRAINT_NAME, "offer_criterion", type_="foreignkey")
    op.create_foreign_key(CONSTRAINT_NAME, "offer_criterion", "offer", ["offerId"], ["id"], ondelete="CASCADE")


def downgrade():
    op.drop_constraint(CONSTRAINT_NAME, "offer_criterion", type_="foreignkey")
    op.create_foreign_key(CONSTRAINT_NAME, "offer_criterion", "offer", ["offerId"], ["id"])
