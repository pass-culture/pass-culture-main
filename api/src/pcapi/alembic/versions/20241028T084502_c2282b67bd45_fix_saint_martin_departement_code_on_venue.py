"""Fix venue.departementCode for venues in Saint-Martin"""

from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "c2282b67bd45"
down_revision = "58750d92ea20"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute("""SET SESSION statement_timeout = '600s'""")
    op.execute(
        # Test: 0.215s on staging
        """
        UPDATE venue
        SET "departementCode" = '978'
        WHERE "postalCode" = '97150'
    """
    )
    op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")


def downgrade() -> None:
    pass
