"""Add NOT NULL constraint on "user_session.expirationDatetime" (step 1 of 4)"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "40349024b1a5"
down_revision = "3b18271dd413"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE "user_session" DROP CONSTRAINT IF EXISTS "user_session_expirationDatetime_not_null_constraint";
        ALTER TABLE "user_session" ADD CONSTRAINT "user_session_expirationDatetime_not_null_constraint" CHECK ("expirationDatetime" IS NOT NULL) NOT VALID;
        """
    )


def downgrade() -> None:
    op.drop_constraint("user_session_expirationDatetime_not_null_constraint", table_name="user_session")
