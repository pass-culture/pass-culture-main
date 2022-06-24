"""create_venue_educational_status
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "3a02357e17ba"
down_revision = "363db8d498a7"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "venue_educational_status",
        sa.Column("id", sa.BigInteger(), autoincrement=False, nullable=False),
        sa.Column("name", sa.String(length=256), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.add_column("venue", sa.Column("venueEducationalStatusId", sa.BigInteger(), nullable=True))
    op.create_foreign_key(
        "venue_educational_status_venue_fkey", "venue", "venue_educational_status", ["venueEducationalStatusId"], ["id"]
    )


def downgrade() -> None:
    op.drop_constraint("venue_educational_status_venue_fkey", "venue", type_="foreignkey")
    op.drop_column("venue", "venueEducationalStatusId")
    op.drop_table("venue_educational_status")
