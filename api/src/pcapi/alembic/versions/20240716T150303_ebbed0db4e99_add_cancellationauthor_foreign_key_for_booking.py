"""
add cancellationAuthor to booking foreignkey
"""

from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "ebbed0db4e99"
down_revision = "7ed9516f7af7"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    if not settings.IS_PROD:
        op.create_foreign_key(
            "booking_cancellation_author_fk",
            "booking",
            "user",
            ["cancellationAuthorId"],
            ["id"],
            postgresql_not_valid=True,
        )


def downgrade() -> None:
    if not settings.IS_PROD:
        op.drop_constraint("booking_cancellation_author_fk", "booking", type_="foreignkey")
