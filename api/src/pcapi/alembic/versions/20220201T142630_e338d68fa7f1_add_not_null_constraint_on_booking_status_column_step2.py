"""add_not_null_constraint_on_booking_status_column_step2
"""
from alembic import op

from pcapi import settings


# revision identifiers, used by Alembic.


revision = "e338d68fa7f1"
down_revision = "1fbaca679195"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("COMMIT")
    op.execute(
        """
        SET SESSION statement_timeout = '900s'
        """
    )
    op.execute("ALTER TABLE booking VALIDATE CONSTRAINT status_not_null_constraint;")
    op.execute(
        f"""
            SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}
            """
    )


def downgrade():
    pass
