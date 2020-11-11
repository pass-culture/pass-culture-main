"""create_iris_venues

Revision ID: b8edbf51e278
Revises: 3e44b9ad4478
Create Date: 2020-03-03 16:47:20.970043

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "b8edbf51e278"
down_revision = "3e44b9ad4478"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "iris_venues",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column("irisId", sa.BigInteger),
        sa.Column("venueId", sa.BigInteger),
    )


def downgrade():
    op.drop_table("iris_venues")
