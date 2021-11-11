"""Update BeneficiaryStatus type to varchar
"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "2d5bcf0c4a22"
down_revision = "ee90200aa0db"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("ALTER TYPE importstatus ADD VALUE  IF NOT EXISTS 'DRAFT'")
    op.execute("ALTER TYPE importstatus ADD VALUE  IF NOT EXISTS 'ONGOING'")
    op.execute("ALTER TYPE importstatus ADD VALUE  IF NOT EXISTS 'WITHOUT_CONTINUATION'")


def downgrade():
    op.execute("ALTER TYPE importstatus RENAME TO importstatus_to_drop")
    op.execute("CREATE TYPE importstatus AS ENUM ('DUPLICATE', 'ERROR', 'CREATED', 'REJECTED', 'RETRY')")
    op.execute(
        (
            'ALTER TABLE beneficiary_import_status ALTER COLUMN "status" TYPE importstatus USING '
            '"beneficiary_import_status"::text::importstatus'
        )
    )
    op.execute("DROP TYPE importstatus_to_drop")
