"""
add cancellationAuthor to booking foreignkey
"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "d630dda4aec6"
down_revision = "e199b0790783"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.create_foreign_key(
        "booking_cancellation_author_fk",
        "booking",
        "user",
        ["cancellationAuthorId"],
        ["id"],
        postgresql_not_valid=True,
    )


def downgrade() -> None:
    op.drop_constraint("booking_cancellation_author_fk", "booking", type_="foreignkey")
