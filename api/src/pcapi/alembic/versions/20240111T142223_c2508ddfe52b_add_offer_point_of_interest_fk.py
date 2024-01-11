"""Add Offer.PointOfInterestId column
"""
from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "c2508ddfe52b"
down_revision = "7e365d8d301b"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("offer", sa.Column("pointOfInterestId", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "offer_pointOfInterestId_fkey",
        "offer",
        "point_of_interest",
        ["pointOfInterestId"],
        ["id"],
        ondelete="SET NULL",
        postgresql_not_valid=True,
    )


def downgrade() -> None:
    op.drop_constraint("offer_pointOfInterestId_fkey", "offer", type_="foreignkey")
    op.drop_column("offer", "pointOfInterestId")
