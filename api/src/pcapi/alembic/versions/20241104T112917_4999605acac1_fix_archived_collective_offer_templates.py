"""Fix archived collective offer templates"""

from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "4999605acac1"
down_revision = "464e20772637"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute("""SET SESSION statement_timeout = '600s'""")
    op.execute(
        # Test: 4 seconds on staging
        """
        UPDATE collective_offer_template
        SET "isActive" = false
        WHERE "dateArchived" IS NOT NULL
    """
    )
    op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")


def downgrade() -> None:
    pass
