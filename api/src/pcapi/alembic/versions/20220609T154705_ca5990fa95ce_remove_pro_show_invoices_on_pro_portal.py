"""remove_pro_show_invoices_on_pro_portal
"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "01e4e1b7f714"
down_revision = "0511102bcb21"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("DELETE FROM feature WHERE name = 'SHOW_INVOICES_ON_PRO_PORTAL'")


def downgrade() -> None:
    op.execute(
        """
        INSERT INTO feature (name, description, "isActive")
        VALUES ('SHOW_INVOICES_ON_PRO_PORTAL', 'Activer l''affichage des remboursements sur le portail pro', True)
        """
    )
