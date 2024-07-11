"""
add cancellationAuthor to collective booking foreignkey
"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "123f19c226df"
down_revision = "d630dda4aec6"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.create_foreign_key(
        "collective_booking_cancellation_author_fk",
        "collective_booking",
        "user",
        ["cancellationAuthorId"],
        ["id"],
        postgresql_not_valid=True,
    )


def downgrade() -> None:
    op.drop_constraint("collective_booking_cancellation_author_fk", "collective_booking", type_="foreignkey")
