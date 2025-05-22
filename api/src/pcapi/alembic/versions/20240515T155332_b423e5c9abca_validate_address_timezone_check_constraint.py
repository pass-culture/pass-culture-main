"""Validate Address.timezone check length constraint"""

from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "b423e5c9abca"
down_revision = "fbe025155bfa"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute("""ALTER TABLE address VALIDATE CONSTRAINT "address_timezone_check" """)


def downgrade() -> None:
    # Nothing to downgrade
    pass
