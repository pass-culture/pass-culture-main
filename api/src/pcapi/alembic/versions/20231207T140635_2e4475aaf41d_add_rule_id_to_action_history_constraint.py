"""Add ruleId to ActionHistory constraint
"""
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "2e4475aaf41d"
down_revision = "ea442da9e07f"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_constraint("check_at_least_one_resource_or_is_fraud_action", "action_history")
    op.create_check_constraint(
        "check_action_resource",
        "action_history",
        'num_nonnulls("userId", "offererId", "venueId", "financeIncidentId", "bankAccountId", "ruleId") >= 1 OR "actionType" = \'BLACKLIST_DOMAIN_NAME\' OR "actionType" = \'REMOVE_BLACKLISTED_DOMAIN_NAME\' OR "actionType" = \'ROLE_PERMISSIONS_CHANGED\'',
    )


def downgrade() -> None:
    op.drop_constraint("check_action_resource", "action_history")
    op.create_check_constraint(
        "check_at_least_one_resource_or_is_fraud_action",
        "action_history",
        'num_nonnulls("userId", "offererId", "venueId", "financeIncidentId", "bankAccountId") >= 1 OR "actionType" = \'BLACKLIST_DOMAIN_NAME\' OR "actionType" = \'REMOVE_BLACKLISTED_DOMAIN_NAME\' OR "actionType" = \'ROLE_PERMISSIONS_CHANGED\'',
    )
