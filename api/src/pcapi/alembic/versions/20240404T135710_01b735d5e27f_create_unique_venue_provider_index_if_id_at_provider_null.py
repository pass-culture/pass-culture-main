"""create unique venue provider index if venue id at provider is null"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "01b735d5e27f"
down_revision = "0dc3123e5ede"


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.create_index(
            "unique_venue_provider_index_null_venue_id_at_provider",
            "venue_provider",
            ["venueId", "providerId"],
            unique=True,
            postgresql_concurrently=True,
            if_not_exists=True,
            postgresql_where=sa.text('"venueIdAtOfferProvider" IS NULL'),
        )


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.drop_index(
            "unique_venue_provider_index_null_venue_id_at_provider",
            table_name="venue_provider",
            if_exists=True,
            postgresql_concurrently=True,
        )
