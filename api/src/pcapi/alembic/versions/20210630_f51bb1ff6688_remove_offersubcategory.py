"""remove_offersubcategory

Revision ID: f51bb1ff6688
Revises: 61b7c21523b0
Create Date: 2021-06-30 14:20:53.785229

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "f51bb1ff6688"
down_revision = "61b7c21523b0"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_table("offer_subcategory")


def downgrade():
    op.create_table(
        "offer_subcategory",
        sa.Column("isActive", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("categoryId", sa.Integer(), nullable=False),
        sa.Column("isEvent", sa.Boolean(), nullable=False),
        sa.Column("proLabel", sa.Text(), nullable=False),
        sa.Column("appLabel", sa.Text(), nullable=False),
        sa.Column("conditionalFields", postgresql.ARRAY(sa.Text()), nullable=True),
        sa.Column("canExpire", sa.Boolean(), nullable=False),
        sa.Column("isDigital", sa.Boolean(), nullable=False),
        sa.Column("isDigitalDeposit", sa.Boolean(), nullable=False),
        sa.Column("isPhysicalDeposit", sa.Boolean(), nullable=False),
        sa.Column("canBeDuo", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(
            ["categoryId"],
            ["offer_category.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("appLabel"),
        sa.UniqueConstraint("name"),
        sa.UniqueConstraint("proLabel"),
    )
