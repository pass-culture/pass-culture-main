"""delete offerer_stats table unique constraint on table and offerer
"""
from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "7049d737cb3f"
down_revision = "9ed959b8d025"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_constraint("offerer_stats_unique", "offerer_stats", type_="unique")


def downgrade() -> None:
    op.create_unique_constraint("offerer_stats_unique", "offerer_stats", ["offererId", "table"])
