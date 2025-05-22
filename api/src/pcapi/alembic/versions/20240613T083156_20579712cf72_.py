"""
validate constraint discord_user_userId_fkey
"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "20579712cf72"
down_revision = "e4cd12df4552"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute("""ALTER TABLE discord_user VALIDATE CONSTRAINT "discord_user_userId_fkey" """)


def downgrade() -> None:
    pass
