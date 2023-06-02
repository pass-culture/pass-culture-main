"""
add dateCreated to collective_offer_request
"""
from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "cf9c67b851f6"
down_revision = "69ef0222cdc8"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "collective_offer_request",
        sa.Column("dateCreated", sa.Date(), server_default=sa.text("CURRENT_DATE"), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("collective_offer_request", "dateCreated")
