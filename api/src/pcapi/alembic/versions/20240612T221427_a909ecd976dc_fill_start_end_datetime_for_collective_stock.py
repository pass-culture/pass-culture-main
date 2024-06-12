"""Fill CollectiveStock's startDatetime and endDatetime
"""

from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "a909ecd976dc"
down_revision = "12f6f068d2bc"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        UPDATE collective_stock SET "startDatetime" = "beginningDatetime" WHERE "startDatetime" IS NULL
        """
    )
    op.execute(
        """
        UPDATE collective_stock SET "endDatetime" = "beginningDatetime" WHERE "endDatetime" IS NULL
        """
    )


def downgrade() -> None:
    pass
