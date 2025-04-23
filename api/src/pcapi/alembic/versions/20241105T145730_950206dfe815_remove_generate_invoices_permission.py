"""Remove GENERATE_INVOICES permission"""

from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "950206dfe815"
down_revision = "a973a6b8c819"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute(
        """DELETE FROM role_permission WHERE role_permission."permissionId" =(SELECT id FROM permission p WHERE p.name = 'GENERATE_INVOICES');"""
    )
    op.execute("""DELETE FROM permission WHERE permission.name = 'GENERATE_INVOICES';""")


def downgrade() -> None:
    pass
