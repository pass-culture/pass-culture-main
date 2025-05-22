"""Add NOT NULL constraint on user_account_update_request."dsTechnicalId" (step 4 of 4)"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "83e0ea9a1587"
down_revision = "cc9a939003aa"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute(
        'ALTER TABLE "user_account_update_request" DROP CONSTRAINT IF EXISTS "ds_technical_id_not_null_constraint";'
    )


def downgrade() -> None:
    op.execute(
        """ALTER TABLE "user_account_update_request" ADD CONSTRAINT "ds_technical_id_not_null_constraint" CHECK ("dsTechnicalId" IS NOT NULL) NOT VALID;"""
    )
