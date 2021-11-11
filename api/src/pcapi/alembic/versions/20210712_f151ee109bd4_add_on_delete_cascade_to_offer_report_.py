"""add_on_delete_cascade_to_offer_report_offer_id_and_user_id

Revision ID: f151ee109bd4
Revises: 5c5141274495
Create Date: 2021-07-12 12:29:19.528478

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "f151ee109bd4"
down_revision = "5c5141274495"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_constraint("offer_report_userId_fkey", "offer_report", type_="foreignkey")
    op.drop_constraint("offer_report_offerId_fkey", "offer_report", type_="foreignkey")
    op.create_foreign_key(None, "offer_report", "user", ["userId"], ["id"], ondelete="CASCADE")
    op.create_foreign_key(None, "offer_report", "offer", ["offerId"], ["id"], ondelete="CASCADE")


def downgrade():
    op.drop_constraint("offer_report_offerId_fkey", "offer_report", type_="foreignkey")
    op.drop_constraint("offer_report_userId_fkey", "offer_report", type_="foreignkey")
    op.create_foreign_key("offer_report_offerId_fkey", "offer_report", "offer", ["offerId"], ["id"])
    op.create_foreign_key("offer_report_userId_fkey", "offer_report", "user", ["userId"], ["id"])
