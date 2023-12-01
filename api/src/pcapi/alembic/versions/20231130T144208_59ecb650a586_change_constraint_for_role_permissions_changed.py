"""Add ROLE_PERMISSIONS_CHANGED to action history constraint
"""
from alembic import op


revision = "59ecb650a586"
down_revision = "b6a4121a0971"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_constraint("check_at_least_one_resource_or_is_fraud_action", "action_history")
    op.create_check_constraint(
        "check_at_least_one_resource_or_is_fraud_action",
        "action_history",
        'num_nonnulls("userId", "offererId", "venueId", "financeIncidentId", "bankAccountId") >= 1 OR "actionType" = \'BLACKLIST_DOMAIN_NAME\' OR "actionType" = \'REMOVE_BLACKLISTED_DOMAIN_NAME\' OR "actionType" = \'ROLE_PERMISSIONS_CHANGED\'',
    )


def downgrade() -> None:
    op.drop_constraint("check_at_least_one_resource_or_is_fraud_action", "action_history")
    op.create_check_constraint(
        "check_at_least_one_resource_or_is_fraud_action",
        "action_history",
        'num_nonnulls("userId", "offererId", "venueId", "financeIncidentId", "bankAccountId") >= 1 OR "actionType" = \'BLACKLIST_DOMAIN_NAME\' OR "actionType" = \'REMOVE_BLACKLISTED_DOMAIN_NAME\'',
    )
