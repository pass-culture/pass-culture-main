"""Add NOT NULL constraint on user_account_update_request."dsTechnicalId" (step 2 of 4)"""

from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "378a6eed6341"
down_revision = "6c644b6bd07d"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute("SET SESSION statement_timeout = '300s'")
        op.execute(
            'ALTER TABLE "user_account_update_request" VALIDATE CONSTRAINT "ds_technical_id_not_null_constraint"'
        )
        op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")


def downgrade() -> None:
    op.execute("ALTER TABLE user_account_update_request DROP CONSTRAINT IF EXISTS ds_technical_id_not_null_constraint")
