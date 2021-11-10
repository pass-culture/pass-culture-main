"""add_not_null_venue_provider_venue_id_at_offer_provider_step_2
"""
from alembic import op

# revision identifiers, used by Alembic.
from pcapi import settings


revision = "010aba57cb3e"
down_revision = "a0a822d365ac"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("COMMIT")
    op.execute(
        """
        SET SESSION statement_timeout = '900s'
        """
    )
    op.execute("ALTER TABLE venue_provider VALIDATE CONSTRAINT venueid_at_offer_provider_not_null_constraint;")
    op.execute(
        f"""
        SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}
        """
    )


def downgrade():
    pass
