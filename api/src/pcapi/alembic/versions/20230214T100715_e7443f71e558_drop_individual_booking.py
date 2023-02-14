"""drop_individual_booking
"""
from alembic import op
import sqlalchemy as sa


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "e7443f71e558"
down_revision = "b8b34e5a2e5b"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_constraint("individual_booking_depositId_fkey", "individual_booking", type_="foreignkey")
    op.drop_constraint("individual_booking_userId_fkey", "individual_booking", type_="foreignkey")
    op.drop_table("individual_booking")


def downgrade() -> None:
    op.create_table(
        "individual_booking",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("userId", sa.BigInteger(), nullable=False),
        sa.Column("depositId", sa.BigInteger(), nullable=True),
        sa.ForeignKeyConstraint(["userId"], ["user.id"]),
        sa.ForeignKeyConstraint(["depositId"], ["deposit.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_individual_booking_depositId"), "individual_booking", ["depositId"], unique=False)
    op.create_index(op.f("ix_individual_booking_userId"), "individual_booking", ["userId"], unique=False)
