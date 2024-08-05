"""
add cancellationAuthor for collective_booking
"""

# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "35d67a2cddcd"
down_revision = "5f46232cb72f"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
