"""Add finance incident to ActionHistory table
"""
from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "72fa9c444b5a"
down_revision = "117312f339eb"
branch_labels = None
depends_on = None

fk_constaint_name = "action_history_incident_fkey"


def upgrade() -> None:
    op.add_column("action_history", sa.Column("financeIncidentId", sa.BigInteger(), nullable=True))
    op.create_index(op.f("ix_action_history_financeIncidentId"), "action_history", ["financeIncidentId"], unique=False)
    op.create_foreign_key(
        fk_constaint_name, "action_history", "finance_incident", ["financeIncidentId"], ["id"], ondelete="CASCADE"
    )

    op.drop_constraint("check_at_least_one_resource_or_is_fraud_action", "action_history")
    op.create_check_constraint(
        "check_at_least_one_resource_or_is_fraud_action",
        "action_history",
        'num_nonnulls("userId", "offererId", "venueId", "financeIncidentId") >= 1 OR "actionType" = \'BLACKLIST_DOMAIN_NAME\' OR "actionType" = \'REMOVE_BLACKLISTED_DOMAIN_NAME\'',
    )


def downgrade() -> None:
    op.drop_constraint("check_at_least_one_resource_or_is_fraud_action", "action_history")
    op.drop_constraint(fk_constaint_name, "action_history", type_="foreignkey")
    op.drop_index(op.f("ix_action_history_financeIncidentId"), table_name="action_history")
    op.drop_column("action_history", "financeIncidentId")
    op.create_check_constraint(
        "check_at_least_one_resource_or_is_fraud_action",
        "action_history",
        'num_nonnulls("userId", "offererId", "venueId") >= 1 OR "actionType" = \'BLACKLIST_DOMAIN_NAME\' OR "actionType" = \'REMOVE_BLACKLISTED_DOMAIN_NAME\'',
    )
