"""Remove exclusion constraint on overlapping custom reimbursement rules."""
from alembic import op


# revision identifiers, used by Alembic.
revision = "0261c634e632"
down_revision = "19a51bd2cf55"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_constraint("custom_reimbursement_rule_offerId_timespan_excl", "custom_reimbursement_rule")


def downgrade():
    op.create_exclude_constraint(
        "custom_reimbursement_rule_offerId_timespan_excl",
        "custom_reimbursement_rule",
        ("offerId", "="),
        ("timespan", "&&"),
    )
