"""
revert adding cancellationAuthorId column on booking and collective_booking
"""

# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "227228152465"
down_revision = "4bd28b6d5d6c"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
