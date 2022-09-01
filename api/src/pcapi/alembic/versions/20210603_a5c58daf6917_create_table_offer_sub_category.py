"""create table offer_subcategory

Revision ID: a5c58daf6917
Revises: 2861278ffd7d
Create Date: 2021-06-03 13:46:05.488861

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "a5c58daf6917"
down_revision = "2861278ffd7d"
branch_labels = None
depends_on = None


def upgrade():
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


def downgrade():
    op.drop_table("offer_subcategory")
