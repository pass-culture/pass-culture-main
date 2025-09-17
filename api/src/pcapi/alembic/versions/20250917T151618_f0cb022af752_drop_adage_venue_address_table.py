"""Drop adage_venue_address table"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "f0cb022af752"
down_revision = "7ad93a37b8f0"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.drop_table("adage_venue_address")


def downgrade() -> None:
    op.create_table(
        "adage_venue_address",
        sa.Column("id", sa.BIGINT(), autoincrement=True, nullable=False),
        sa.Column("adageId", sa.TEXT(), autoincrement=False, nullable=True),
        sa.Column("adageInscriptionDate", postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
        sa.Column("venueId", sa.BIGINT(), autoincrement=False, nullable=True),
        sa.ForeignKeyConstraint(
            ["venueId"], ["venue.id"], name=op.f("adage_venue_address_venueId_fkey"), ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("adage_venue_address_pkey")),
        sa.UniqueConstraint("adageId", name=op.f("adage_venue_address_adageId_key")),
    )
    with op.get_context().autocommit_block():
        op.create_index(
            op.f("ix_adage_venue_address_venueId"),
            "adage_venue_address",
            ["venueId"],
            unique=False,
            if_not_exists=True,
            postgresql_concurrently=True,
        )
