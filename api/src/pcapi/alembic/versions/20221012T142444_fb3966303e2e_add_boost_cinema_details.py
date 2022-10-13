"""add boost_cinema_details (PRE)"""
from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "fb3966303e2e"
down_revision = "b1f1858336c2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "boost_cinema_details",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("cinemaProviderPivotId", sa.BigInteger(), nullable=True),
        sa.Column("cinemaUrl", sa.Text(), nullable=False),
        sa.Column("username", sa.Text(), nullable=False),
        sa.Column("password", sa.Text(), nullable=False),
        sa.Column("token", sa.Text(), nullable=True),
        sa.Column("tokenExpirationDate", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["cinemaProviderPivotId"],
            ["cinema_provider_pivot.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("cinemaProviderPivotId"),
    )


def downgrade() -> None:
    op.drop_table("boost_cinema_details")
