"""
add cancellationAuthor to booking foreignkey
"""

from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "4dcee336192f"
down_revision = "4bd28b6d5d6c"
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
