"""add validation_type.CGU_INCOMPATIBLE_PRODUCT enum value
"""
from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "2967ed08d3e0"
down_revision = "46ab023fbf0f"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TYPE validation_type ADD VALUE 'CGU_INCOMPATIBLE_PRODUCT'")


def downgrade() -> None:
    op.execute("ALTER TYPE validation_type RENAME TO validation_type_old")
    op.execute("CREATE TYPE validation_type AS ENUM('AUTO','MANUAL')")
    op.execute(
        (
            'ALTER TABLE offer ALTER COLUMN "lastValidationType" TYPE validation_type USING '
            '"lastValidationType"::text::validation_type'
        )
    )
    op.execute(
        (
            'ALTER TABLE collective_offer ALTER COLUMN "lastValidationType" TYPE validation_type USING '
            '"lastValidationType"::text::validation_type'
        )
    )
    op.execute(
        (
            'ALTER TABLE collective_offer_template ALTER COLUMN "lastValidationType" TYPE validation_type USING '
            '"lastValidationType"::text::validation_type'
        )
    )
    op.execute("DROP TYPE validation_type_old")
