"""add table allocine_venue_registry
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "e3aae72aab7f"
down_revision = "64d4d0dabdd2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "allocine_theater",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("siret", sa.String(length=14), nullable=True),
        sa.Column("theaterId", sa.String(length=20), nullable=False),
        sa.Column("internalId", sa.Text, nullable=False),
        sa.UniqueConstraint("siret", name="unique_siret"),
        sa.UniqueConstraint("theaterId", name="unique_theater_id"),
        sa.UniqueConstraint("internalId", name="unique_internal_id"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("allocine_theater")
