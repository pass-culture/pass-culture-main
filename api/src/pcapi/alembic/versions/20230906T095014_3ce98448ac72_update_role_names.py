""" Update Role names with new names defined in Roles enum
"""
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "3ce98448ac72"
down_revision = "9d1128058b6d"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("UPDATE role SET name = 'support_n1' WHERE name = 'support-N1'")
    op.execute("UPDATE role SET name = 'support_n2' WHERE name = 'support-N2'")
    op.execute("UPDATE role SET name = 'support_pro' WHERE name = 'support-PRO'")
    op.execute("UPDATE role SET name = 'support_pro_n2' WHERE name = 'support-PRO-N2'")
    op.execute("UPDATE role SET name = 'partenaire_technique' WHERE name = 'bizdev'")
    op.execute("UPDATE role SET name = 'programmation_market' WHERE name = 'programmation'")
    op.execute("UPDATE role SET name = 'responsable_daf' WHERE name = 'responsable-daf'")
    op.execute("UPDATE role SET name = 'charge_developpement' WHERE name = 'charge-developpement'")
    op.execute("UPDATE role SET name = 'lecture_seule' WHERE name = 'lecture-seule'")
    op.execute("UPDATE role SET name = 'product_management' WHERE name = 'product-management'")
    op.execute("UPDATE role SET name = 'fraude_jeunes' WHERE name = 'fraude-jeunes'")
    op.execute("UPDATE role SET name = 'fraude_conformite' WHERE name = 'fraude-conformite'")
    op.execute("UPDATE role SET name = 'global_access' WHERE name = 'global-access'")


def downgrade() -> None:
    op.execute("UPDATE role SET name = 'support-N1' WHERE name = 'support_n1'")
    op.execute("UPDATE role SET name = 'support-N2' WHERE name = 'support_n2'")
    op.execute("UPDATE role SET name = 'support-PRO' WHERE name = 'support_pro'")
    op.execute("UPDATE role SET name = 'support-PRO-N2' WHERE name = 'support_pro_n2'")
    op.execute("UPDATE role SET name = 'bizdev' WHERE name = 'partenaire_technique'")
    op.execute("UPDATE role SET name = 'programmation' WHERE name = 'programmation_market'")
    op.execute("UPDATE role SET name = 'responsable-daf' WHERE name = 'responsable_daf'")
    op.execute("UPDATE role SET name = 'charge-developpement' WHERE name = 'charge_developpement'")
    op.execute("UPDATE role SET name = 'lecture-seule' WHERE name = 'lecture_seule'")
    op.execute("UPDATE role SET name = 'product-management' WHERE name = 'product_management'")
    op.execute("UPDATE role SET name = 'fraude-jeunes' WHERE name = 'fraude_jeunes'")
    op.execute("UPDATE role SET name = 'fraude-conformite' WHERE name = 'fraude_conformite'")
    op.execute("UPDATE role SET name = 'global-access' WHERE name = 'global_access'")
