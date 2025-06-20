"""Update foreign key user_account_update_request.userId: on delete set null (2/2)"""

from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "4b97dba7262f"
down_revision = "a35242268279"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute("SET SESSION statement_timeout='300s'")
    op.execute(
        """ALTER TABLE user_account_update_request VALIDATE CONSTRAINT "user_account_update_request_userId_fkey" """
    )
    op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")


def downgrade() -> None:
    pass
