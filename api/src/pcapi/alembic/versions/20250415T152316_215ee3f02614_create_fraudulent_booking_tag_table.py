"""Create FraudulentBookingTag table"""

from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "215ee3f02614"
down_revision = "e9c8d83f71ce"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.create_table(
        "fraudulent_booking_tag",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("dateCreated", sa.DateTime(), nullable=False),
        sa.Column("bookingId", sa.BigInteger(), nullable=False),
        sa.Column("authorId", sa.BigInteger(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_fraudulent_booking_tag_authorId"), "fraudulent_booking_tag", ["authorId"], unique=False)
    op.create_index(op.f("ix_fraudulent_booking_tag_bookingId"), "fraudulent_booking_tag", ["bookingId"], unique=True)


def downgrade() -> None:
    op.drop_table("fraudulent_booking_tag")
