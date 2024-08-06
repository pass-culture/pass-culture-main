"""
add cancellationUser to collective booking foreignkey
"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "84359b3cc978"
down_revision = "b0b1f2a95d61"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.create_foreign_key(
        "collective_booking_cancellation_user_fk",
        "collective_booking",
        "user",
        ["cancellationUserId"],
        ["id"],
        postgresql_not_valid=True,
    )


def downgrade() -> None:
    op.drop_constraint("collective_booking_cancellation_user_fk", "collective_booking", type_="foreignkey")
