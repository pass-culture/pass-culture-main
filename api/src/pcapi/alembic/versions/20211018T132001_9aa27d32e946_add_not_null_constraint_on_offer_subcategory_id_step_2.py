"""add_not_null_constraint_on_offer_subcategory_id_step_2
"""
from alembic import op

from pcapi import settings


# revision identifiers, used by Alembic.
revision = "9aa27d32e946"
down_revision = "2db527b06f6b"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("COMMIT")
    op.execute(
        """
        SET SESSION statement_timeout = '900s'
        """
    )
    op.execute("ALTER TABLE offer VALIDATE CONSTRAINT subcategory_id_not_null_constraint;")
    op.execute(
        f"""
        SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}
        """
    )


def downgrade():
    pass
