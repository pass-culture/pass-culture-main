"""Validate "proAdvicesCount" check constraint on "product" table"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "4f7546074f71"
down_revision = "b7c0f6b89749"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute("""ALTER TABLE "product" VALIDATE CONSTRAINT "check_pro_advices_count_is_positive" """)


def downgrade() -> None:
    pass
