"""create_educational_year_table

Revision ID: f0cad4632e56
Revises: 86f064fa42a7
Create Date: 2021-06-28 10:49:07.794556

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "f0cad4632e56"
down_revision = "86f064fa42a7"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "educational_year",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("beginningDate", sa.DateTime(), nullable=False),
        sa.Column("expirationDate", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade():
    op.drop_table("educational_year")
