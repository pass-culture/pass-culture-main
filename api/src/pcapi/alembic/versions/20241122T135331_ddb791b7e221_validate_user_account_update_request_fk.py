"""Validate constraint on user_account_update_request.userId and user_account_update_request.lastInstructorId"""

from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "ddb791b7e221"
down_revision = "9bca134a0476"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute("SET SESSION statement_timeout = '300s'")
    op.execute(
        """ALTER TABLE user_account_update_request VALIDATE CONSTRAINT "user_account_update_request_userId_fkey" """
    )
    op.execute(
        """ALTER TABLE user_account_update_request VALIDATE CONSTRAINT "user_account_update_request_lastInstructorId_fkey" """
    )
    op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")


def downgrade() -> None:
    pass
