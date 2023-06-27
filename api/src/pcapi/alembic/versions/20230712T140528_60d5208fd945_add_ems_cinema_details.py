"""Add EMS cinema details table"""
from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "60d5208fd945"
down_revision = "c1c137b863fe"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "ems_cinema_details",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("cinemaProviderPivotId", sa.BigInteger(), nullable=True),
        sa.Column("lastVersion", sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(
            ["cinemaProviderPivotId"],
            ["cinema_provider_pivot.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("cinemaProviderPivotId"),
    )


def downgrade() -> None:
    op.drop_table("ems_cinema_details")
