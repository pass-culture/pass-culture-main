"""add_not_null_constraint_on_product_subcategory_id_step_2
"""
from alembic import op

from pcapi import settings


# revision identifiers, used by Alembic.
revision = "d6028fa2c32b"
down_revision = "00da19d9eaae"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("COMMIT")
    op.execute(
        """
        SET SESSION statement_timeout = '900s'
        """
    )
    op.execute("ALTER TABLE product VALIDATE CONSTRAINT subcategory_id_not_null_constraint;")
    op.execute(
        f"""
        SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}
        """
    )


def downgrade():
    pass
