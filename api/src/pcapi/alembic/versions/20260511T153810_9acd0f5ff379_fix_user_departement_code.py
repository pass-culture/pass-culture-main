"""fix user.departementCode in Corsica"""

from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "9acd0f5ff379"
down_revision = "451508fb2262"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    # Test on staging: 78.541s
    op.execute("SET SESSION statement_timeout='600s'")
    op.execute(
        """UPDATE "user" set "departementCode" = public.postal_code_to_department_code("postalCode") WHERE "departementCode" = '20';"""
    )
    op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")


def downgrade() -> None:
    op.execute("SET SESSION statement_timeout='600s'")
    op.execute("""UPDATE "user" set "departementCode" = '20' WHERE "departementCode" IN ('2A', '2B');""")
    op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")
