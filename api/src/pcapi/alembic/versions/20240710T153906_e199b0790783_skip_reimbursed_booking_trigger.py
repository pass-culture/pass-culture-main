"""Skip check_booking function trigger when setting the status field's value to REIMBURSED
"""

from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "e199b0790783"
down_revision = "361fc0a4ba9b"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    if not settings.IS_PROD:
        op.execute("DROP TRIGGER IF EXISTS booking_update ON booking")
        op.execute(
            """CREATE CONSTRAINT TRIGGER booking_update
AFTER INSERT
OR UPDATE OF quantity, amount, status, "userId"
ON booking
FOR EACH ROW
WHEN (NEW.status <> 'REIMBURSED')
EXECUTE PROCEDURE check_booking()"""
        )


def downgrade() -> None:
    if not settings.IS_PROD:
        op.execute("DROP TRIGGER IF EXISTS booking_update ON booking")
        op.execute(
            """CREATE CONSTRAINT TRIGGER booking_update
AFTER INSERT
OR UPDATE OF quantity, amount, status, "userId"
ON booking
FOR EACH ROW EXECUTE PROCEDURE check_booking()"""
        )
