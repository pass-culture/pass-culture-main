"""remove_offercategory

Revision ID: b59aa6de9662
Revises: f51bb1ff6688
Create Date: 2021-06-30 14:24:17.295088

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "b59aa6de9662"
down_revision = "f51bb1ff6688"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_table("offer_category")


def downgrade():
    op.create_table(
        "offer_category",
        sa.Column("isActive", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("proLabel", sa.Text(), nullable=False),
        sa.Column("appLabel", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("appLabel"),
        sa.UniqueConstraint("name"),
        sa.UniqueConstraint("proLabel"),
    )
