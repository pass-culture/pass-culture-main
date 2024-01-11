"""Add Venue.PointOfInterestId column
"""
from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "6672bb132441"
down_revision = "757ce6c389fd"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("venue", sa.Column("pointOfInterestId", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "venue_pointOfInterestId_fkey",
        "venue",
        "point_of_interest",
        ["pointOfInterestId"],
        ["id"],
        ondelete="SET NULL",
        postgresql_not_valid=True,
    )


def downgrade() -> None:
    op.drop_constraint("venue_pointOfInterestId_fkey", "venue", type_="foreignkey")
    op.drop_column("venue", "pointOfInterestId")
