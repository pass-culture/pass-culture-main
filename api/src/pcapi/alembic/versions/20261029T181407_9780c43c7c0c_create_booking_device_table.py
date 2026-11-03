"""Create booking_device table."""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "9780c43c7c0c"
down_revision = "8674a7978007"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.create_table(
        "booking_device",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("bookingId", sa.BigInteger(), nullable=False),
        sa.Column("deviceId", sa.Text(), nullable=True),
        sa.Column("os", sa.Text(), nullable=True),
        sa.Column("source", sa.Text(), nullable=True),
        sa.Column("ipAddress", postgresql.INET(), nullable=True),
        sa.Column("dateCreated", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["bookingId"], ["booking.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("bookingId"),
        sa.CheckConstraint(
            'masklen("ipAddress") = CASE family("ipAddress") WHEN 4 THEN 32 ELSE 128 END',
            name="booking_device_single_ip_address_constraint",
        ),
        if_not_exists=True,
    )


def downgrade() -> None:
    op.drop_table("booking_device", if_exists=True)
