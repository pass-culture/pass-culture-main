"""validate idAtProvider check constraint to offer
"""
from alembic import op

from pcapi import settings


# revision identifiers, used by Alembic.
revision = "28a13156d2d8"
down_revision = "fafc5b6c2398"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("COMMIT")
    op.execute(
        """
        SET SESSION statement_timeout = '300s'
        """
    )
    op.execute("ALTER TABLE offer VALIDATE CONSTRAINT check_providable_with_provider_has_idatprovider;")
    op.execute(
        f"""
        SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}
        """
    )


def downgrade() -> None:
    pass
