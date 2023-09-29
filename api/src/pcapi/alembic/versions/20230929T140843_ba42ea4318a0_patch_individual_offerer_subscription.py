"""Finally remove targetsCollectiveOffers and targetsIndividualOffers from individual_offerer_subscription table
"""
from alembic import op
import sqlalchemy as sa


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "ba42ea4318a0"
down_revision = "e0ed8316241a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_column("individual_offerer_subscription", "targetsCollectiveOffers")
    op.drop_column("individual_offerer_subscription", "targetsIndividualOffers")


def downgrade() -> None:
    op.add_column(
        "individual_offerer_subscription",
        sa.Column(
            "targetsIndividualOffers",
            sa.BOOLEAN(),
            server_default=sa.text("false"),
            autoincrement=False,
            nullable=False,
        ),
    )
    op.add_column(
        "individual_offerer_subscription",
        sa.Column(
            "targetsCollectiveOffers",
            sa.BOOLEAN(),
            server_default=sa.text("false"),
            autoincrement=False,
            nullable=False,
        ),
    )
