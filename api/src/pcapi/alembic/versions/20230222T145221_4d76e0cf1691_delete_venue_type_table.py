"""delete_venue_type_table
"""
from alembic import op
import sqlalchemy as sa


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "4d76e0cf1691"
down_revision = "329eb64be6c5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_constraint("venue_venueTypeId_fkey", "venue", type_="foreignkey")
    op.drop_column("venue", "venueTypeId")
    op.drop_table("venue_type")


def downgrade() -> None:
    op.add_column("venue", sa.Column("venueTypeId", sa.INTEGER(), autoincrement=False, nullable=True))
    op.create_table(
        "venue_type",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("label", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_foreign_key("venue_venueTypeId_fkey", "venue", "venue_type", ["venueTypeId"], ["id"])
