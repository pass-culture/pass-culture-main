"""remove_offer_venueId_idAtProvider_index
"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "d159acbab4a7"
down_revision = "e07f81517c8a"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_constraint("offer_idAtProviders_key", table_name="offer")
    op.create_unique_constraint(
        "unique_venueId_and_idAtProviders_in_offer", table_name="offer", columns=["venueId", "idAtProviders"]
    )


def downgrade():
    op.drop_constraint("unique_venueId_and_idAtProviders_in_offer", table_name="offer")
    op.create_unique_constraint("offer_idAtProviders_key", table_name="offer", columns=["idAtProviders"])
