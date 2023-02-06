"""openning_6_5
"""
from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "d184cbdaadd5"
down_revision = "44f8313b7321"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TYPE studentlevels ADD VALUE 'COLLEGE5'")
    op.execute("ALTER TYPE studentlevels ADD VALUE 'COLLEGE6'")


def downgrade() -> None:
    op.execute("ALTER TYPE studentlevels RENAME TO studentlevels_old")
    op.execute(
        "CREATE TYPE studentlevels AS ENUM('COLLEGE4', 'COLLEGE3', 'CAP1', 'CAP2', 'GENERAL2', 'GENERAL1', 'GENERAL0')"
    )
    # collective_offer
    op.execute('ALTER TABLE collective_offer ALTER COLUMN "students" TYPE text[];')
    op.execute("""ALTER TABLE collective_offer ALTER COLUMN "students" SET DEFAULT '{}'::text[];""")
    op.execute("""ALTER TABLE collective_offer ALTER COLUMN "students" SET DEFAULT '{}'::studentlevels[];""")
    op.execute(
        ('ALTER TABLE collective_offer ALTER COLUMN "students" TYPE studentlevels[] USING "students"::studentlevels[]')
    )
    # collective_offer_template
    op.execute('ALTER TABLE collective_offer_template ALTER COLUMN "students" TYPE text[];')
    op.execute("""ALTER TABLE collective_offer_template ALTER COLUMN "students" SET DEFAULT '{}'::text[];""")
    op.execute("""ALTER TABLE collective_offer_template ALTER COLUMN "students" SET DEFAULT '{}'::studentlevels[];""")
    op.execute(
        (
            'ALTER TABLE collective_offer_template ALTER COLUMN "students" TYPE studentlevels[] USING "students"::studentlevels[]'
        )
    )
    # venue
    op.execute('ALTER TABLE venue ALTER COLUMN "collectiveStudents" TYPE text[];')
    op.execute("""ALTER TABLE venue ALTER COLUMN "collectiveStudents" SET DEFAULT '{}'::text[];""")
    op.execute("""ALTER TABLE venue ALTER COLUMN "collectiveStudents" SET DEFAULT '{}'::studentlevels[];""")
    op.execute(
        (
            'ALTER TABLE venue ALTER COLUMN "collectiveStudents" TYPE studentlevels[] USING "collectiveStudents"::studentlevels[]'
        )
    )
    op.execute("DROP TYPE studentlevels_old")
