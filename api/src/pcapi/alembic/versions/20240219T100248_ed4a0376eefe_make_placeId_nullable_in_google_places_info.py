"""
Make placeId nullable in google_places_info

"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "ed4a0376eefe"
down_revision = "e9ed5b8f1267"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column("google_places_info", "placeId", existing_type=sa.TEXT(), nullable=True)


def downgrade() -> None:
    # we delete the rows with a null value to stay commpatible with previous versions of code
    # since these lins where not recorded
    googe_places_info_table = sa.table("google_places_info", sa.column("placeId"))
    sa.delete(googe_places_info_table).where(googe_places_info_table.c.placeId is None)
    op.alter_column("google_places_info", "placeId", existing_type=sa.TEXT(), nullable=False)
