"""Add new ValidationStatus.CLOSED"""

from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "8ee08df65b28"
down_revision = "1b5deb8e094c"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute("ALTER TYPE validationstatus ADD VALUE 'CLOSED'")
    op.execute("select 1 -- squawk:ignore-next-statement")
    op.execute(
        'ALTER TABLE offerer ALTER COLUMN "validationStatus" TYPE validationstatus USING '
        '"validationStatus"::text::validationstatus'
    )
    op.execute("select 1 -- squawk:ignore-next-statement")
    op.execute(
        'ALTER TABLE user_offerer ALTER COLUMN "validationStatus" TYPE validationstatus USING '
        '"validationStatus"::text::validationstatus'
    )


def downgrade() -> None:
    op.execute("ALTER TYPE validationstatus RENAME TO validationstatus_old")
    op.execute("CREATE TYPE validationstatus AS ENUM ('NEW', 'PENDING', 'VALIDATED', 'REJECTED', 'DELETED')")
    op.execute("select 1 -- squawk:ignore-next-statement")
    op.execute(
        'ALTER TABLE offerer ALTER COLUMN "validationStatus" TYPE validationstatus USING '
        '"validationStatus"::text::validationstatus'
    )
    op.execute("select 1 -- squawk:ignore-next-statement")
    op.execute(
        'ALTER TABLE user_offerer ALTER COLUMN "validationStatus" TYPE validationstatus USING '
        '"validationStatus"::text::validationstatus'
    )
    op.execute("DROP TYPE validationstatus_old")
