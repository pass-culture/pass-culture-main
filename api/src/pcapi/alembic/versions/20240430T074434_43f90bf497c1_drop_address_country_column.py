"""Drop Address.country column"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "43f90bf497c1"
down_revision = "3fe28059d41c"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute("""ALTER TABLE "address" DROP COLUMN IF EXISTS "country" """)


def downgrade() -> None:
    # We don't want to add a not nullable column in downgrade migration
    pass
