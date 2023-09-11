"""add new validation status DELETED for relation user-offerer
"""
from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "1f3334d5aee5"
down_revision = "f2f67d2fb7f3"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TYPE validationstatus ADD VALUE 'DELETED'")
    op.execute(
        'ALTER TABLE user_offerer ALTER COLUMN "validationStatus" TYPE validationstatus USING '
        '"validationStatus"::text::validationstatus'
    )
    op.execute(
        'ALTER TABLE offerer ALTER COLUMN "validationStatus" TYPE validationstatus USING '
        '"validationStatus"::text::validationstatus'
    )


def downgrade() -> None:
    op.execute("ALTER TYPE validationstatus RENAME TO validationstatus_old")
    op.execute("CREATE TYPE validationstatus AS ENUM ('NEW', 'PENDING', 'VALIDATED', 'REJECTED')")
    op.execute(
        'ALTER TABLE user_offerer ALTER COLUMN "validationStatus" TYPE validationstatus USING '
        '"validationStatus"::text::validationstatus'
    )
    op.execute(
        'ALTER TABLE offerer ALTER COLUMN "validationStatus" TYPE validationstatus USING '
        '"validationStatus"::text::validationstatus'
    )
    op.execute("DROP TYPE validationstatus_old")
