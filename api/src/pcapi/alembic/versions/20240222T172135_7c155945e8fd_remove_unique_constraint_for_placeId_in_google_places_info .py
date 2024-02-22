"""
Remove unique constraint for placeId from google_places_info
"""

from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "7c155945e8fd"
down_revision = "ed4a0376eefe"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_constraint("google_places_info_placeId_key", "google_places_info", type_="unique")


def downgrade() -> None:
    # In general it's better to use concurrently when adding a unique constraint.
    # but in our case the table is only modified once a month.
    # thus it's ok to ignore the warning.
    # we also do not implement the removal of double entries.
    # Due to the complexity and the rare usecase when the downgrade will face this problem
    op.execute("select 1 -- squawk:ignore-next-statement")
    op.create_unique_constraint("google_places_info_placeId_key", "google_places_info", ["placeId"])
