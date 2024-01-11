"""Add OffererPointofInterest.OffererId foreign key
"""
from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "d4d4d6006520"
down_revision = "e76924b370af"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("offerer_point_of_interest", sa.Column("offererId", sa.Integer(), nullable=True))
    op.create_index(
        "ix_unique_poi_usage_per_offerer", "offerer_point_of_interest", ["offererId", "pointOfInterestId"], unique=True
    )
    op.create_foreign_key(
        "offerer_point_of_interest_offererId_fkey",
        "offerer_point_of_interest",
        "offerer",
        ["offererId"],
        ["id"],
        postgresql_not_valid=True,
    )


def downgrade() -> None:
    op.drop_constraint("offerer_point_of_interest_offererId_fkey", "offerer_point_of_interest", type_="foreignkey")
    op.drop_index("ix_unique_poi_usage_per_offerer", table_name="offerer_point_of_interest")
    op.drop_column("offerer_point_of_interest", "offererId")
