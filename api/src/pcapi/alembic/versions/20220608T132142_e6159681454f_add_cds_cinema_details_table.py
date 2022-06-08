"""add cds_cinema_details table (PRE-deploy)"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "e6159681454f"
down_revision = "0447eb830b16"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "cds_cinema_details",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("cinemaProviderPivotId", sa.BigInteger(), nullable=True),
        sa.Column("cinemaApiToken", sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(
            ["cinemaProviderPivotId"],
            ["cinema_provider_pivot.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("cinemaProviderPivotId"),
    )


def downgrade():
    op.drop_table("cds_cinema_details")
