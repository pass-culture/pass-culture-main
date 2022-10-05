"""add index on user.validatedBirthDate
"""
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "8ab2b534c85b"
down_revision = "7fd5994a51aa"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("COMMIT")
    op.execute(
        """
        CREATE INDEX CONCURRENTLY IF NOT EXISTS "ix_user_validatedBirthDate" ON "user" ("validatedBirthDate")
        """
    )


def downgrade() -> None:
    op.execute("COMMIT")
    op.drop_index("ix_user_validatedBirthDate", table_name="user")
