"""add adage venue address model"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "381fef70eb7a"
down_revision = "d3bd3af52558"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "adage_venue_address",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("adageId", sa.Text(), nullable=True),
        sa.Column("adageInscriptionDate", sa.DateTime(), nullable=True),
        sa.Column("venueId", sa.BigInteger(), nullable=True),
        sa.ForeignKeyConstraint(
            ["venueId"],
            ["venue.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("adageId"),
    )
    op.create_index(op.f("ix_adage_venue_address_venueId"), "adage_venue_address", ["venueId"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_adage_venue_address_venueId"), table_name="adage_venue_address")
    op.drop_table("adage_venue_address")
