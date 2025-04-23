"""Add NOT NULL constraint on user_account_update_request."dsTechnicalId" (step 1 of 4)"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "6c644b6bd07d"
down_revision = "d9b82f286880"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE "user_account_update_request" DROP CONSTRAINT IF EXISTS "ds_technical_id_not_null_constraint";
        ALTER TABLE "user_account_update_request" ADD CONSTRAINT "ds_technical_id_not_null_constraint" CHECK ("dsTechnicalId" IS NOT NULL) NOT VALID;
        """
    )


def downgrade() -> None:
    op.execute("ALTER TABLE user_account_update_request DROP CONSTRAINT IF EXISTS ds_technical_id_not_null_constraint")
