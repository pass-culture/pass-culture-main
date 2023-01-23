"""add cgr_cinema_details table"""
from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "fa7c663db77a"
down_revision = "1eab834f493d"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "cgr_cinema_details",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("cinemaProviderPivotId", sa.BigInteger(), nullable=True),
        sa.Column("cinemaUrl", sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(
            ["cinemaProviderPivotId"],
            ["cinema_provider_pivot.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("cinemaProviderPivotId"),
    )


def downgrade() -> None:
    op.drop_table("cgr_cinema_details")
