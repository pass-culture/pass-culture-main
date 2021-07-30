"""Add individual booking model

Revision ID: 888f037beae1
Revises: 19b36a0b880a
Create Date: 2021-07-28 14:01:20.412664

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "888f037beae1"
down_revision = "19b36a0b880a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "individual_booking",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("userId", sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(
            ["userId"],
            ["user.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_individual_booking_userId"), "individual_booking", ["userId"], unique=False)
    op.add_column("booking", sa.Column("individualBookingId", sa.BigInteger(), nullable=True))
    op.create_foreign_key(None, "booking", "individual_booking", ["individualBookingId"], ["id"])


def downgrade() -> None:
    op.drop_constraint(None, "booking", type_="foreignkey")
    op.drop_column("booking", "individualBookingId")
    op.drop_index(op.f("ix_individual_booking_userId"), table_name="individual_booking")
    op.drop_table("individual_booking")
