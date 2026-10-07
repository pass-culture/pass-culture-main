"""Add column: fraudulent_booking_tag.venueId"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "c8cbc38c2bad"
down_revision = "18cf42ac9ab5"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.add_column("fraudulent_booking_tag", sa.Column("venueId", sa.BigInteger(), nullable=True))
    op.create_foreign_key(
        "fraudulent_booking_tag_venue_fk",
        "fraudulent_booking_tag",
        "venue",
        ["venueId"],
        ["id"],
        postgresql_not_valid=True,
    )


def downgrade() -> None:
    op.drop_constraint("fraudulent_booking_tag_venue_fk", "fraudulent_booking_tag", type_="foreignkey")
    op.drop_column("fraudulent_booking_tag", "venueId")
