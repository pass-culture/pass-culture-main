"""Fix archived collective offers"""

from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "6519c3689ae8"
down_revision = "4999605acac1"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute("""SET SESSION statement_timeout = '600s'""")
    op.execute(
        # Test: 16 seconds on staging
        """
        UPDATE collective_offer
        SET "isActive" = false
        WHERE "dateArchived" IS NOT NULL
    """
    )
    op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")


def downgrade() -> None:
    pass
