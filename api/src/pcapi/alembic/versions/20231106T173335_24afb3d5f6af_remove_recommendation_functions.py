"""Remove old recommendation-related functions"""
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "24afb3d5f6af"
down_revision = "4110ad29566e"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("drop function if exists event_is_in_less_than_10_days(bigint)")
    op.execute("drop function if exists get_offer_score(bigint)")
    op.execute("drop function if exists get_active_offers_ids(boolean)")
    op.execute("drop function if exists offer_has_at_least_one_active_mediation(bigint)")
    op.execute("drop function if exists offer_has_at_least_one_bookable_stock(bigint)")


def downgrade() -> None:
    pass  # no rollback, these functions really are unused
