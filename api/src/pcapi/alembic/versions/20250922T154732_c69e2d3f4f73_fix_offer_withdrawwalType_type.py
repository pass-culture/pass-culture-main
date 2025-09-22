"""fix offer.withdrawalType type"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "c69e2d3f4f73"
down_revision = "671f97131193"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute("select 1 -- squawk:ignore-next-statement")
    op.execute('ALTER TABLE  offer ALTER COLUMN "withdrawalType" TYPE TEXT;')


def downgrade() -> None:
    op.execute("select 1 -- squawk:ignore-next-statement")
    op.execute('ALTER TABLE  offer ALTER COLUMN "withdrawalType" TYPE VARCHAR;')
