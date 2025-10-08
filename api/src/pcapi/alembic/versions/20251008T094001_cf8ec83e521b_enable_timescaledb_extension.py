"""Enable TimescaleDB extension"""

from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "cf8ec83e521b"
down_revision = "b717eddfe468"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS timescaledb;")


def downgrade() -> None:
    op.execute("DROP EXTENSION IF EXISTS timescaledb;")
