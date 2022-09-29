"""add_has_seen_offer_duplication_modal_to_user_model
"""
from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "2c5900b6e16e"
down_revision = "e3d81633703f"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "user", sa.Column("hasSeenOfferDuplicationModal", sa.Boolean(), server_default=sa.text("false"), nullable=False)
    )


def downgrade() -> None:
    op.drop_column("user", "hasSeenOfferDuplicationModal")
