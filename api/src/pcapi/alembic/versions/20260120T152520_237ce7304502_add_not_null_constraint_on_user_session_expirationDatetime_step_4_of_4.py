"""Add NOT NULL constraint on "user_session.expirationDatetime" (step 4 of 4)"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "237ce7304502"
down_revision = "3d993db2a1f2"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.drop_constraint("user_session_expirationDatetime_not_null_constraint", table_name="user_session")


def downgrade() -> None:
    op.execute(
        """ALTER TABLE "user_session" ADD CONSTRAINT "user_session_expirationDatetime_not_null_constraint" CHECK ("expirationDatetime" IS NOT NULL) NOT VALID"""
    )
