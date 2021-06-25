"""remove_subcategory_fk_from_offer

Revision ID: 61b7c21523b0
Revises: 6c410aedecbd
Create Date: 2021-06-30 09:24:39.542439

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "61b7c21523b0"
down_revision = "6c410aedecbd"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_index("ix_offer_subcategoryId", table_name="offer")
    op.drop_constraint("offer_subcategoryId_fkey", "offer", type_="foreignkey")
    op.drop_column("offer", "subcategoryId")


def downgrade():
    op.add_column("offer", sa.Column("subcategoryId", sa.BIGINT(), autoincrement=False, nullable=True))
    op.create_foreign_key("offer_subcategoryId_fkey", "offer", "offer_subcategory", ["subcategoryId"], ["id"])
    op.create_index("ix_offer_subcategoryId", "offer", ["subcategoryId"], unique=False)
