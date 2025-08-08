"""Add NOT NULL constraint on "artist.is_blacklisted" (step 3 of 4)"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "3d913bae7e96"
down_revision = "a538858d9a48"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.alter_column("artist", "is_blacklisted", nullable=False)


def downgrade() -> None:
    op.alter_column("artist", "is_blacklisted", nullable=True)
