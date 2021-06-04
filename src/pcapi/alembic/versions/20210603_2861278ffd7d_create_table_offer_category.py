"""create table offer_category

Revision ID: 2861278ffd7d
Revises: 32bea863ac77
Create Date: 2021-06-03 13:31:37.479586

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "2861278ffd7d"
down_revision = "2a24a51d4735"
branch_labels = None
depends_on = None


def upgrade():
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


def downgrade():
    op.drop_table("offer_category")
