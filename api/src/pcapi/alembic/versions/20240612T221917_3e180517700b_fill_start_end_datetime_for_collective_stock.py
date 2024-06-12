"""Fill CollectiveStock's startDatetime and endDatetime
"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "3e180517700b"
down_revision = "0126d932677e"
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
