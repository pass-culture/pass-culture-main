"""Create index: ix_offerer_address_unique_venue_location_per_venue_id"""

import sqlalchemy as sa
from alembic import op

from pcapi import settings

# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "2cb884d0afc9"
down_revision = "9a9d34c60788"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute("SET SESSION statement_timeout='300s'")
        op.create_index(
            "ix_offerer_address_unique_venue_location_per_venue_id",
            "offerer_address",
            ["venueId"],
            unique=True,
            postgresql_where=sa.text("type = 'VENUE_LOCATION'"),
            postgresql_concurrently=True,
            if_not_exists=True,
        )
        op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.drop_index(
            "ix_offerer_address_unique_venue_location_per_venue_id",
            table_name="offerer_address",
            postgresql_concurrently=True,
            if_exists=True,
        )
