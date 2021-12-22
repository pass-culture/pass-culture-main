"""Add reference_scheme table."""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "e07f81517c8a"
down_revision = "d71dd05eae76"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "reference_scheme",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("prefix", sa.Text(), nullable=False),
        sa.Column("year", sa.Integer(), nullable=True),
        sa.Column("nextNumber", sa.Integer(), nullable=True),
        sa.Column("numberPadding", sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name", "year", name="unique_name_year"),
        sa.UniqueConstraint("prefix", "year", name="unique_prefix_year"),
    )


def downgrade():
    op.drop_table("reference_scheme")
