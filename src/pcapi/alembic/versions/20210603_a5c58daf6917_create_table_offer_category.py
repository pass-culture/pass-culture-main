"""create table offer_category

Revision ID: a5c58daf6917
Revises: 2861278ffd7d
Create Date: 2021-06-03 13:46:05.488861

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "a5c58daf6917"
down_revision = "2861278ffd7d"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "offer_category",
        sa.Column("isActive", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("categoryGroupId", sa.Integer(), nullable=False),
        sa.Column("isEvent", sa.Boolean(), nullable=False),
        sa.Column("proLabel", sa.Text(), nullable=False),
        sa.Column("appLabel", sa.Text(), nullable=False),
        sa.Column("conditionalFields", sa.ARRAY(sa.Text()), nullable=True),
        sa.Column("canExpire", sa.Boolean(), nullable=False),
        sa.Column("isDigital", sa.Boolean(), nullable=False),
        sa.Column("digitalDeposit", sa.Boolean(), nullable=False),
        sa.Column("physicalDeposit", sa.Boolean(), nullable=False),
        sa.Column("canBeDuo", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(
            ["categoryGroupId"],
            ["offer_category_group.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("appLabel"),
        sa.UniqueConstraint("name"),
        sa.UniqueConstraint("proLabel"),
    )


def downgrade():
    op.drop_table("offer_category")
