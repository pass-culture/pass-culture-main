"""
add cancellationAuthor to collective booking foreignkey
"""

# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "9118d1848c98"
down_revision = "ebbed0db4e99"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
