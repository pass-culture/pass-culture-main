"""
add cancellationAuthor to collective booking foreignkey
"""

from alembic import op
import sqlalchemy as sa


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "41fa3e5e4a10"
down_revision = "4dcee336192f"
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
