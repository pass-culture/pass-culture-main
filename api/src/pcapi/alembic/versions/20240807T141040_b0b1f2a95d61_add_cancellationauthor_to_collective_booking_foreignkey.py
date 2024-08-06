"""
add cancellationUser to collective booking foreignkey
"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "b0b1f2a95d61"
down_revision = "03013c06a0ac"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.create_foreign_key(
        "booking_cancellation_user_fk",
        "booking",
        "user",
        ["cancellationUserId"],
        ["id"],
        postgresql_not_valid=True,
    )


def downgrade() -> None:
    op.drop_constraint("booking_cancellation_user_fk", "booking", type_="foreignkey")
