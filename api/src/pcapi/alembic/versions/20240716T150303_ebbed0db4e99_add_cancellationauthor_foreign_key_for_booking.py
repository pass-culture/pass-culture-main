"""
add cancellationAuthor to booking foreignkey
"""

# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "ebbed0db4e99"
down_revision = "7ed9516f7af7"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
