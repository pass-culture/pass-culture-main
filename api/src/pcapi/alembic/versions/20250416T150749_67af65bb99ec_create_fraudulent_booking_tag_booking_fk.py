"""Create FraudulentBookingTag booking foreign key constraint
"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "67af65bb99ec"
down_revision = "b4eb9ea33b3e"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.create_foreign_key(
        "fraudulent_booking_tag_booking_fk",
        "fraudulent_booking_tag",
        "booking",
        ["bookingId"],
        ["id"],
        postgresql_not_valid=True,
    )


def downgrade() -> None:
    op.drop_constraint("fraudulent_booking_tag_booking_fk", "fraudulent_booking_tag", type_="foreignkey")
