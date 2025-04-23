"""Create FraudulentBookingTag user foreign key constraint"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "b0b1ec888d1b"
down_revision = "377710c191ca"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.create_foreign_key(
        "fraudulent_booking_tag_author_fk",
        "fraudulent_booking_tag",
        "user",
        ["authorId"],
        ["id"],
        postgresql_not_valid=True,
    )


def downgrade() -> None:
    op.drop_constraint("fraudulent_booking_tag_author_fk", "fraudulent_booking_tag", type_="foreignkey")
