"""Delete NOT NULL constraints on postal code and city in Offerer table, and on timezone in Venue table"""

from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "e429a884bfe0"
down_revision = "b717eddfe468"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.alter_column("offerer", "postalCode", nullable=True)
    op.alter_column("offerer", "city", nullable=True)
    op.alter_column("venue", "timezone", nullable=True)


def downgrade() -> None:
    op.alter_column("offerer", "postalCode", nullable=False)
    op.alter_column("offerer", "city", nullable=False)
    op.alter_column("venue", "timezone", nullable=False)
